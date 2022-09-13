import contextlib
import os.path
from typing import Dict
from typing import Generator
from typing import List
from typing import Set

from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.downloaders.downloader import download_logger
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.entry_parent import EntryParent
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.validators import ListValidator
from ytdl_sub.validators.validators import StringValidator


def _entry_key(entry: Entry) -> str:
    return entry.extractor + entry.uid


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
        self, source_variables: List[str], override_variables: List[str]
    ) -> None:
        """
        Ensures new variables added are not existing variables
        """
        # TODO: Make sure they resolve
        for added_source_var in self.added_source_variables():
            if added_source_var in source_variables:
                raise self._validation_exception(
                    f"'{added_source_var}' cannot be used as a variable name because it "
                    f"is an existing source variable"
                )


class CollectionDownloader(Downloader[CollectionDownloadOptions, Entry]):
    downloader_options_type = CollectionDownloadOptions
    downloader_entry_type = Entry

    def _recursive_child_read(
        self, collection_url: CollectionUrlValidator, parent: EntryParent, entry_dicts: List[Dict]
    ) -> List[Entry]:
        leaf_children: List[Entry] = []
        parent.read_nested_children_from_entry_dicts(entry_dicts=entry_dicts)

        for idx in range(parent.child_count):
            child: EntryParent = parent.child_entries[idx]

            leaf_children.extend(
                self._recursive_child_read(
                    collection_url=collection_url, parent=child, entry_dicts=entry_dicts
                )
            )

            # If the child has no nested children, turn it into an Entry
            if not child.child_count:
                parent.child_entries[idx] = child.to_entry()
                leaf_children.append(parent.child_entries[idx])

        for leaf_child in leaf_children:
            leaf_child.add_variables(parent.get_children_entry_variables_to_add())
            leaf_child.add_variables(collection_url.variables)

        return leaf_children

    def _get_leaf_entries(self, collection_url: CollectionUrlValidator) -> List[Entry]:
        # Dry-run to get the info json files
        # TODO: Mock the download
        entry_dicts = self.extract_info_via_info_json(
            only_info_json=True,
            url=collection_url.url,
        )

        # initialize top-level parents, determined by whether a playlist_id exists in the entry dict
        parents: List[EntryParent] = [
            EntryParent(entry_dict=entry_dict, working_directory=self.working_directory)
            for entry_dict in entry_dicts
            if "playlist_id" not in entry_dict
        ]

        leaf_children: List[Entry] = []
        for parent in parents:
            leaf_children.extend(
                self._recursive_child_read(
                    collection_url=collection_url, parent=parent, entry_dicts=entry_dicts
                )
            )

        return leaf_children

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

    def _download_leaf_entry(self, entry: Entry) -> Entry:
        download_logger.info("Downloading entry %s", entry.title)

        # TODO: Mock the download archive if dry-run
        if not self.is_dry_run:
            download_entry_dict = self.extract_info_with_retry(
                is_downloaded_fn=entry.is_downloaded,
                url=entry.webpage_url,
                ytdl_options_overrides={"writeinfojson": False},
            )

            # Workaround for the ytdlp issue
            # pylint: disable=protected-access
            entry._kwargs["requested_subtitles"] = download_entry_dict.get("requested_subtitles")
            # pylint: enable=protected-access

        return entry

    def _download_collection_url(
        self, collection_url: CollectionUrlValidator, downloaded_entries: Set[str]
    ) -> Generator[Entry, None, None]:
        with self._separate_download_archives():
            leaf_children = [
                leaf
                for leaf in self._get_leaf_entries(collection_url)
                if _entry_key(leaf) not in downloaded_entries
            ]

            # Reverse leaf_children downloads so we download older entries first
            for leaf in reversed(leaf_children):
                yield self._download_leaf_entry(entry=leaf)
                downloaded_entries.add(_entry_key(leaf))

    def download(self) -> Generator[Entry, None, None]:
        """
        Soundcloud subscription to download albums and tracks as singles.
        """
        downloaded_entries: Set[str] = set()

        # download the bottom-most urls first since they are top-priority
        for collection_url in reversed(self.download_options.collection_urls.list):
            for entry in self._download_collection_url(
                collection_url=collection_url, downloaded_entries=downloaded_entries
            ):
                yield entry
