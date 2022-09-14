import contextlib
import os.path
from typing import Dict
from typing import Generator
from typing import List
from typing import Set

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderOptionsT
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.downloaders.downloader import download_logger
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.entry_parent import EntryParent
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import ListValidator
from ytdl_sub.validators.validators import StringValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


def _entry_key(entry: BaseEntry) -> str:
    return entry.extractor + entry.uid


def _get_parent_entry_variables(parent: EntryParent) -> Dict[str, str | int]:
    """
    Adds source variables to the child entry derived from the parent entry.
    """
    if not parent.child_entries:
        return {}

    return {
        "playlist_max_upload_year": max(
            child_entry.to_type(Entry).upload_year for child_entry in parent.child_entries
        )
    }


class CollectionUrlValidator(StrictDictValidator):
    _required_keys = {"url"}
    _optional_keys = {"variables"}

    def __init__(self, name, value):
        super().__init__(name, value)

        # TODO: url validate using yt-dlp IE
        self._url = self._validate_key(key="url", validator=StringValidator)
        variables = self._validate_key_if_present(key="variables", validator=DictFormatterValidator)
        self._variables = variables.dict_with_format_strings if variables else {}

    @property
    def url(self) -> str:
        """
        Returns
        -------
        URL to download from
        """
        return self._url.value

    @property
    def variables(self) -> Dict[str, str]:
        """
        Variables to add to each entry
        """
        return self._variables


class CollectionUrlListValidator(ListValidator[CollectionUrlValidator]):
    _inner_list_type = CollectionUrlValidator
    _expected_value_type_name = "collection url list"

    def __init__(self, name, value):
        super().__init__(name, value)

        added_variables: Dict[str, str] = self.list[0].variables

        for idx, collection_url_validator in enumerate(self.list[1:]):
            collection_variables = collection_url_validator.variables

            # see if this collection contains new added vars (it should not)
            for var in collection_variables.keys():
                if var not in added_variables:
                    raise self._validation_exception(
                        f"Collection url {idx} contains the variable '{var}' that the first "
                        f"collection url does not. The first collection url must define all added "
                        f"variables."
                    )

            # see if this collection is missing any added vars (if so, inherit from the top)
            for var in added_variables.keys():
                if var not in collection_variables:
                    collection_variables[var] = added_variables[var]


class CollectionDownloadOptions(DownloaderValidator):
    """
    Downloads from multiple URLs. If an entry is returned from more than one URL, it will
    resolve to the bottom-most URL settings.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          generic:
            # required
            download_strategy: "collection"
            urls:
            - url: "soundcloud.com/tracks"
              variables:
                season: "1"
                album: "{title}"
            - url: "soundcloud.com/albums"
              variables:
                season: "1"
                album: "{playlist_title}"
    """

    _required_keys = {"urls"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._urls = self._validate_key(key="urls", validator=CollectionUrlListValidator)

    @property
    def collection_urls(self) -> CollectionUrlListValidator:
        """
        Required. The Soundcloud user's url, i.e. ``soundcloud.com/the_username``
        """
        return self._urls

    def added_source_variables(self) -> List[str]:
        """
        Returns
        -------
        List of variables added. The first collection url always contains all the variables.
        """
        return list(self._urls.list[0].variables.keys())

    def validate_with_variables(
        self, source_variables: List[str], override_variables: Dict[str, str]
    ) -> None:
        """
        Ensures new variables added are not existing variables
        """
        for source_var_name in self.added_source_variables():
            if source_var_name in source_variables:
                raise self._validation_exception(
                    f"'{source_var_name}' cannot be used as a variable name because it "
                    f"is an existing source variable"
                )

        base_variables = dict(
            override_variables, **{source_var: "dummy_string" for source_var in source_variables}
        )

        # Apply formatting to each new source variable, ensure it resolves
        for collection_url in self.collection_urls.list:
            for source_var_name, source_var_formatter_str in collection_url.variables.items():
                _ = StringFormatterValidator(
                    name=f"{self._name}.{source_var_name}", value=source_var_formatter_str
                ).apply_formatter(base_variables)


class CollectionDownloader(Downloader[CollectionDownloadOptions, Entry]):
    downloader_options_type = CollectionDownloadOptions
    downloader_entry_type = Entry

    def __init__(
        self,
        download_options: DownloaderOptionsT,
        enhanced_download_archive: EnhancedDownloadArchive,
        ytdl_options_builder: YTDLOptionsBuilder,
        overrides: Overrides,
    ):
        super().__init__(
            download_options=download_options,
            enhanced_download_archive=enhanced_download_archive,
            ytdl_options_builder=ytdl_options_builder,
            overrides=overrides,
        )

        self.parents: List[EntryParent] = []
        self.downloaded_entries: Set[str] = set()

    @contextlib.contextmanager
    def _separate_download_archives(self):
        """
        Separate download archive writing between collection urls. This is so break_on_existing
        does not break when downloading from subset urls.
        """
        archive_path = self._ytdl_options_builder.to_dict().get("download_archive", "")
        backup_archive_path = f"{archive_path}.backup"

        # If archive path exists, maintain download archive is enable
        if archive_file_exists := archive_path and os.path.isfile(archive_path):
            archive_file_exists = True

            # If a backup exists, it's the one prior to any downloading, use that.
            if os.path.isfile(backup_archive_path):
                FileHandler.copy(src_file_path=backup_archive_path, dst_file_path=archive_path)
            # If not, create the backup
            else:
                FileHandler.copy(src_file_path=archive_path, dst_file_path=backup_archive_path)

        yield

        # If an archive path did not exist at first, but now exists, delete it
        if not archive_file_exists and os.path.isfile(archive_path):
            FileHandler.delete(file_path=archive_path)
        # If the archive file did exist, restore the backup
        elif archive_file_exists:
            FileHandler.copy(src_file_path=backup_archive_path, dst_file_path=archive_path)

    def _download_entry(self, entry: Entry) -> Entry:
        download_logger.info("Downloading entry %s", entry.title)
        download_entry_dict = self.extract_info_with_retry(
            is_downloaded_fn=None if self.is_dry_run else entry.is_downloaded,
            url=entry.webpage_url,
            ytdl_options_overrides={"writeinfojson": False, "skip_download": self.is_dry_run},
        )

        # Workaround for the ytdlp issue
        # pylint: disable=protected-access
        entry._kwargs["requested_subtitles"] = download_entry_dict.get("requested_subtitles")
        # pylint: enable=protected-access

        return entry

    def _download_parent_entry(self, parent: EntryParent) -> Generator[Entry, None, None]:
        """Download in reverse order, that way we download older entries ones first"""
        for entry_child in reversed(parent.entry_children()):
            if _entry_key(entry_child) in self.downloaded_entries:
                continue

            yield self._download_entry(entry_child.to_type(Entry))
            self.downloaded_entries.add(_entry_key(entry_child))

        for parent_child in reversed(parent.parent_children()):
            for entry_child in self._download_parent_entry(parent=parent_child):
                yield entry_child

    def download_url_metadata(self, collection_url: CollectionUrlValidator) -> List[EntryParent]:
        """
        Downloads only info.json files and forms EntryParent trees
        """
        with self._separate_download_archives():
            entry_dicts = self.extract_info_via_info_json(
                only_info_json=True,
                url=collection_url.url,
                log_prefix_on_info_json_dl="Downloading metadata for",
            )

        return EntryParent.from_entry_dicts(
            entry_dicts=entry_dicts, working_directory=self.working_directory
        )

    def download_url(
        self, collection_url: CollectionUrlValidator, parents: List[EntryParent]
    ) -> Generator[Entry, None, None]:
        """
        Downloads the leaf entries from EntryParent trees
        """
        with self._separate_download_archives():
            for parent in parents:
                for entry_child in self._download_parent_entry(parent=parent):
                    entry_child.add_variables(
                        dict(_get_parent_entry_variables(parent), **collection_url.variables)
                    )
                    yield entry_child

    def download(self) -> Generator[Entry, None, None]:
        """
        Soundcloud subscription to download albums and tracks as singles.
        """
        # download the bottom-most urls first since they are top-priority
        for collection_url in reversed(self.download_options.collection_urls.list):
            parents = self.download_url_metadata(collection_url=collection_url)
            for entry in self.download_url(collection_url=collection_url, parents=parents):
                yield entry
