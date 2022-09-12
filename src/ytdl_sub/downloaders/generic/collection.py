from typing import Dict
from typing import Generator
from typing import List
from typing import Set

from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.downloaders.downloader import download_logger
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.entry_parent import EntryParent
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
        self._variables = self._validate_key_if_present(
            key="variables", validator=DictFormatterValidator
        ).dict_with_format_strings

    @property
    def url(self) -> str:
        return self._url.value

    @property
    def variables(self) -> Dict[str, str]:
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


class CollectionDownloader(Downloader[CollectionDownloadOptions, Entry]):
    downloader_options_type = CollectionDownloadOptions
    downloader_entry_type = Entry

    def _recursive_child_read(
        self, collection_url: CollectionUrlValidator, parent: EntryParent, entry_dicts: List[Dict]
    ) -> List[Entry]:
        leaf_children: List[Entry] = []
        parent.read_children_from_entry_dicts(entry_dicts=entry_dicts, child_class=EntryParent)

        for idx in range(parent.child_count):
            child = parent.child_entries[idx]

            leaf_children.extend(
                self._recursive_child_read(
                    collection_url=collection_url, parent=child, entry_dicts=entry_dicts
                )
            )

            # If the child has no nested children, turn it into an Entry
            if not child.child_count:
                entry = child.to_entry()
                entry.add_variables(collection_url.variables)
                parent.child_entries[idx] = entry

                leaf_children.append(entry)

        return leaf_children

    def _get_leaf_entries(self, collection_url: CollectionUrlValidator) -> List[Entry]:
        # Dry-run to get the info json files
        entry_dicts = self.extract_info_via_info_json(
            only_info_json=True,
            log_prefix_on_info_json_dl="Downloading metadata for",
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

    def _download_leaf_entry(self, entry: Entry):
        download_logger.info("Downloading entry %s", entry.title)
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

        yield entry

    def download(self) -> Generator[Entry, None, None]:
        """
        Soundcloud subscription to download albums and tracks as singles.
        """
        downloaded_leaf_children: Set[str] = set()

        # download the bottom-most urls first since they are top-priority
        for collection_url in reversed(self.download_options.collection_urls.list):
            leaf_children = self._get_leaf_entries(collection_url)

            for child in leaf_children:
                child_key = _entry_key(child)
                if child_key in downloaded_leaf_children:
                    continue

                yield self._download_leaf_entry(entry=child)
                downloaded_leaf_children.add(child_key)
