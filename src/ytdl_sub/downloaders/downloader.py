import abc
import contextlib
import copy
import json
import os
import time
from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import Generator
from typing import Generic
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Type
from typing import TypeVar

import yt_dlp as ytdl
from yt_dlp.utils import ExistingVideoReached
from yt_dlp.utils import RejectedVideoReached

from ytdl_sub.config.preset_options import AddsVariablesMixin
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.downloaders.generic.collection_validator import CollectionThumbnailListValidator
from ytdl_sub.downloaders.generic.collection_validator import CollectionUrlValidator
from ytdl_sub.downloaders.generic.collection_validator import CollectionValidator
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.entry_parent import EntryParent
from ytdl_sub.entries.variables.kwargs import PLAYLIST_ENTRY
from ytdl_sub.entries.variables.kwargs import SOURCE_ENTRY
from ytdl_sub.thread.log_entries_downloaded_listener import LogEntriesDownloadedListener
from ytdl_sub.utils.exceptions import FileNotDownloadedException
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.thumbnail import convert_url_thumbnail
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadArchiver
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

download_logger = Logger.get(name="downloader")


def _entry_key(entry: BaseEntry) -> str:
    return entry.extractor + entry.uid


class DownloaderValidator(StrictDictValidator, AddsVariablesMixin, ABC):
    """
    Placeholder class to define downloader options
    """

    @property
    @abc.abstractmethod
    def collection_validator(self) -> CollectionValidator:
        """
        Returns
        -------
        CollectionValidator
            To determine how the entries are downloaded
        """

    def added_source_variables(self) -> List[str]:
        """
        Returns
        -------
        Added source variables on the collection
        """
        return self.collection_validator.added_source_variables()

    def validate_with_variables(
        self, source_variables: List[str], override_variables: Dict[str, str]
    ) -> None:
        """
        Validates any source variables added by the collection
        """
        self.collection_validator.validate_with_variables(
            source_variables=source_variables, override_variables=override_variables
        )


DownloaderOptionsT = TypeVar("DownloaderOptionsT", bound=DownloaderValidator)
DownloaderEntryT = TypeVar("DownloaderEntryT", bound=Entry)


class Downloader(DownloadArchiver, Generic[DownloaderOptionsT, DownloaderEntryT], ABC):
    """
    Class that interacts with ytdl to perform the download of metadata and content,
    and should translate that to list of Entry objects.
    """

    downloader_options_type: Type[DownloaderValidator] = DownloaderValidator
    downloader_entry_type: Type[Entry] = Entry

    supports_download_archive: bool = True
    supports_subtitles: bool = True
    supports_chapters: bool = True

    _extract_entry_num_retries: int = 5
    _extract_entry_retry_wait_sec: int = 5

    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
        """
        return {"ignoreerrors": True}

    def __init__(
        self,
        download_options: DownloaderOptionsT,
        enhanced_download_archive: EnhancedDownloadArchive,
        ytdl_options_builder: YTDLOptionsBuilder,
        overrides: Overrides,
    ):
        """
        Parameters
        ----------
        download_options
            Options validator for this downloader
        enhanced_download_archive
            Download archive
        ytdl_options_builder
            YTDL options builder
        overrides
            Override variables
        """
        DownloadArchiver.__init__(self=self, enhanced_download_archive=enhanced_download_archive)
        self.download_options = download_options
        self.overrides = overrides

        self._ytdl_options_builder = ytdl_options_builder.clone().add(
            self.ytdl_option_defaults(), before=True
        )

        self.parents: List[EntryParent] = []
        self.downloaded_entries: Dict[str, Entry] = {}

    @contextmanager
    def ytdl_downloader(self, ytdl_options_overrides: Optional[Dict] = None) -> ytdl.YoutubeDL:
        """
        Context manager to interact with yt_dlp.
        """
        ytdl_options = self._ytdl_options_builder.clone().add(ytdl_options_overrides).to_dict()

        download_logger.debug("ytdl_options: %s", str(ytdl_options))
        with Logger.handle_external_logs(name="yt-dlp"):
            with ytdl.YoutubeDL(ytdl_options) as ytdl_downloader:
                yield ytdl_downloader

    @property
    def is_dry_run(self) -> bool:
        """
        Returns
        -------
        True if dry-run is enabled. False otherwise.
        """
        return self._ytdl_options_builder.to_dict().get("skip_download", False)

    def extract_info(self, ytdl_options_overrides: Optional[Dict] = None, **kwargs) -> Dict:
        """
        Wrapper around yt_dlp.YoutubeDL.YoutubeDL.extract_info
        All kwargs will passed to the extract_info function.

        Parameters
        ----------
        ytdl_options_overrides
            Optional. Dict containing ytdl args to override other predefined ytdl args
        **kwargs
            arguments passed directory to YoutubeDL extract_info
        """
        with self.ytdl_downloader(ytdl_options_overrides) as ytdl_downloader:
            return ytdl_downloader.extract_info(**kwargs)

    def extract_info_with_retry(
        self,
        is_downloaded_fn: Optional[Callable[[], bool]] = None,
        ytdl_options_overrides: Optional[Dict] = None,
        **kwargs,
    ) -> Dict:
        """
        Wrapper around yt_dlp.YoutubeDL.YoutubeDL.extract_info
        All kwargs will passed to the extract_info function.

        This should be used when downloading a single entry. Checks if the entry's video
        and thumbnail files exist - retry if they do not.

        Parameters
        ----------
        is_downloaded_fn
            Optional. Function to check if the entry is downloaded
        ytdl_options_overrides
            Optional. Dict containing ytdl args to override other predefined ytdl args
        **kwargs
            arguments passed directory to YoutubeDL extract_info

        Raises
        ------
        FileNotDownloadedException
            If the entry fails to download
        """
        num_tries = 0
        entry_files_exist = False
        copied_ytdl_options_overrides = copy.deepcopy(ytdl_options_overrides)

        while not entry_files_exist and num_tries < self._extract_entry_num_retries:
            entry_dict = self.extract_info(
                ytdl_options_overrides=copied_ytdl_options_overrides, **kwargs
            )
            if is_downloaded_fn is None or is_downloaded_fn():
                return entry_dict

            time.sleep(self._extract_entry_retry_wait_sec)
            num_tries += 1

            # Remove the download archive so it can retry without thinking its already downloaded,
            # even though it is not
            if "download_archive" in copied_ytdl_options_overrides:
                del copied_ytdl_options_overrides["download_archive"]

            if num_tries < self._extract_entry_retry_wait_sec:
                download_logger.debug(
                    "Failed to download entry. Retrying %d / %d",
                    num_tries,
                    self._extract_entry_num_retries,
                )

        error_dict = {"ytdl_options": ytdl_options_overrides, "kwargs": kwargs}
        raise FileNotDownloadedException(
            f"yt-dlp failed to download an entry with these arguments: {error_dict}"
        )

    def _get_entry_dicts_from_info_json_files(self) -> List[Dict]:
        """
        Returns
        -------
        List of all info.json files read as JSON dicts
        """
        entry_dicts: List[Dict] = []
        info_json_paths = [
            Path(self.working_directory) / file_name
            for file_name in os.listdir(self.working_directory)
            if file_name.endswith(".info.json")
        ]

        for info_json_path in info_json_paths:
            with open(info_json_path, "r", encoding="utf-8") as file:
                entry_dicts.append(json.load(file))

        return entry_dicts

    @contextlib.contextmanager
    def _listen_and_log_downloaded_info_json(self, log_prefix: Optional[str]):
        """
        Context manager that starts a separate thread that listens for new .info.json files,
        prints their titles as they appear
        """
        if not log_prefix:
            yield
            return

        info_json_listener = LogEntriesDownloadedListener(
            working_directory=self.working_directory,
            log_prefix=log_prefix,
        )

        info_json_listener.start()

        try:
            yield
        finally:
            info_json_listener.complete = True

    def extract_info_via_info_json(
        self,
        ytdl_options_overrides: Optional[Dict] = None,
        only_info_json: bool = False,
        log_prefix_on_info_json_dl: Optional[str] = None,
        **kwargs,
    ) -> List[Dict]:
        """
        Wrapper around yt_dlp.YoutubeDL.YoutubeDL.extract_info with infojson enabled. Entry dicts
        are extracted via reading all info.json files in the working directory rather than
        from the output of extract_info.

        This allows us to catch RejectedVideoReached and ExistingVideoReached exceptions, and
        simply ignore while still being able to read downloaded entry metadata.

        Parameters
        ----------
        ytdl_options_overrides
            Optional. Dict containing ytdl args to override other predefined ytdl args
        only_info_json
            Default false. Skip download and thumbnail download if True.
        log_prefix_on_info_json_dl
            Optional. Spin a new thread to listen for new info.json files. Log
            f'{log_prefix_on_info_json_dl} {title}' when a new one appears
        **kwargs
            arguments passed directory to YoutubeDL extract_info
        """
        ytdl_options_builder = self._ytdl_options_builder.clone()
        if ytdl_options_overrides is None:
            ytdl_options_overrides = {}

        ytdl_options_builder.add({"writeinfojson": True}, ytdl_options_overrides)
        if only_info_json:
            ytdl_options_builder.add(
                {
                    "skip_download": True,
                    "writethumbnail": False,
                }
            )

        try:
            with self._listen_and_log_downloaded_info_json(log_prefix=log_prefix_on_info_json_dl):
                _ = self.extract_info(
                    ytdl_options_overrides=ytdl_options_builder.to_dict(), **kwargs
                )
        except RejectedVideoReached:
            download_logger.debug("RejectedVideoReached, stopping additional downloads")
        except ExistingVideoReached:
            download_logger.debug("ExistingVideoReached, stopping additional downloads")

        return self._get_entry_dicts_from_info_json_files()

    ###############################################################################################
    # DOWNLOAD FUNCTIONS

    def _is_downloaded(self, entry: Entry) -> bool:
        return _entry_key(entry) in self.downloaded_entries

    def _mark_downloaded(self, entry: Entry) -> None:
        self.downloaded_entries[_entry_key(entry)] = entry

    @property
    def collection(self) -> CollectionValidator:
        """Return the download options collection"""
        return self.download_options.collection_validator

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

    def _download_entries(self, entries: List[Entry]) -> Generator[Entry, None, None]:
        # Download entries in reverse order since they are scraped in the opposite direction.
        # Helps deal with break_on_existing
        for entry in reversed(entries):
            if self._is_downloaded(entry):
                continue

            yield self._download_entry(entry)
            self._mark_downloaded(entry)

    def _download_parent_entry(self, parent: EntryParent) -> Generator[Entry, None, None]:
        for entry_child in self._download_entries(parent.entry_children()):
            yield entry_child

        # Recursion the parent's parent entries
        for parent_child in reversed(parent.parent_children()):
            for entry_child in self._download_parent_entry(parent=parent_child):
                yield entry_child

    def _set_collection_variables(
        self, collection_url: CollectionUrlValidator, entry: Entry | EntryParent
    ):
        if isinstance(entry, EntryParent):
            for child in entry.parent_children():
                self._set_collection_variables(collection_url, child)
            for child in entry.entry_children():
                child.add_variables(variables_to_add=collection_url.variables)

        elif isinstance(entry, Entry):
            entry.add_variables(variables_to_add=collection_url.variables)

    def _download_url_metadata(
        self, collection_url: CollectionUrlValidator
    ) -> Tuple[List[EntryParent], List[Entry]]:
        """
        Downloads only info.json files and forms EntryParent trees
        """
        with self._separate_download_archives():
            entry_dicts = self.extract_info_via_info_json(
                only_info_json=True,
                url=collection_url.url,
                log_prefix_on_info_json_dl="Downloading metadata for",
            )

        self.parents = EntryParent.from_entry_dicts(
            url=collection_url.url,
            entry_dicts=entry_dicts,
            working_directory=self.working_directory,
        )
        orphans = EntryParent.from_entry_dicts_with_no_parents(
            parents=self.parents, entry_dicts=entry_dicts, working_directory=self.working_directory
        )

        for parent_entry in self.parents:
            self._set_collection_variables(collection_url, parent_entry)
        for entry in orphans:
            self._set_collection_variables(collection_url, entry)

        return self.parents, orphans

    def _download(
        self,
        parents: Optional[List[EntryParent]] = None,
        orphans: Optional[List[Entry]] = None,
    ) -> Generator[Entry, None, None]:
        """
        Downloads the leaf entries from EntryParent trees
        """
        if parents is None:
            parents = []
        if orphans is None:
            orphans = []

        with self._separate_download_archives():
            for parent in parents:
                for entry_child in self._download_parent_entry(parent=parent):
                    yield entry_child

            for orphan in self._download_entries(orphans):
                yield self._download_entry(orphan)

    def download(
        self,
    ) -> Iterable[DownloaderEntryT] | Iterable[Tuple[DownloaderEntryT, FileMetadata]]:
        """The function to perform the download of all media entries"""
        # download the bottom-most urls first since they are top-priority
        for collection_url in reversed(self.collection.collection_urls.list):
            parents, orphan_entries = self._download_url_metadata(collection_url=collection_url)
            collection_url_entries: List[Entry] = []

            for entry in self._download(parents=parents, orphans=orphan_entries):
                yield entry
                collection_url_entries.append(entry)

            self._download_url_thumbnails(
                collection_url=collection_url, entries=collection_url_entries
            )

    @classmethod
    def _download_thumbnail(
        cls,
        thumbnail_url: str,
        output_thumbnail_path: str,
    ) -> Optional[bool]:
        """
        Downloads a thumbnail and stores it in the output directory

        Parameters
        ----------
        thumbnail_url:
            Url of the thumbnail
        output_thumbnail_path:
            Path to store the thumbnail after downloading

        Returns
        -------
        True if the thumbnail converted. None if it is missing or failed.
        """
        if not thumbnail_url:
            return None

        return convert_url_thumbnail(
            thumbnail_url=thumbnail_url, output_thumbnail_path=output_thumbnail_path
        )

    def _download_parent_thumbnails(
        self,
        thumbnails_downloaded: Set[str],
        thumbnail_list_info: CollectionThumbnailListValidator,
        entry: Entry,
        parent: EntryParent,
    ) -> Set[str]:
        """
        Downloads and moves channel avatar and banner images to the output directory.
        """
        for thumbnail_info in thumbnail_list_info.list:
            thumbnail_name = self.overrides.apply_formatter(thumbnail_info.name, entry=entry)
            thumbnail_id = self.overrides.apply_formatter(thumbnail_info.uid)

            # alread downloaded
            if thumbnail_name in thumbnails_downloaded:
                continue

            if (thumbnail_url := parent.get_thumbnail_url(thumbnail_id=thumbnail_id)) is None:
                download_logger.warning("TODO: Failed to download channel's avatar image")
                continue

            if self._download_thumbnail(
                thumbnail_url=thumbnail_url,
                output_thumbnail_path=str(Path(self.working_directory) / thumbnail_name),
            ):
                self.save_file(file_name=thumbnail_name)
                thumbnails_downloaded.add(thumbnail_name)
            else:
                download_logger.warning("TODO: Failed to download channel's avatar image")

        return thumbnails_downloaded

    def _download_url_thumbnails(
        self, collection_url: CollectionUrlValidator, entries: List[Entry]
    ):
        """
        After all media entries have been downloaded, post processed, and moved to the output
        directory, run this function. This lets the downloader add any extra files directly to the
        output directory, for things like YT channel image, banner.
        """
        thumbnails_downloaded: Set[str] = set()

        for entry in entries:
            if entry.kwargs_contains(PLAYLIST_ENTRY):
                thumbnails_downloaded = self._download_parent_thumbnails(
                    thumbnails_downloaded=thumbnails_downloaded,
                    thumbnail_list_info=collection_url.playlist_thumbnails,
                    entry=entry,
                    parent=EntryParent(
                        entry.kwargs(PLAYLIST_ENTRY), working_directory=self.working_directory
                    ),
                )

            if entry.kwargs_contains(SOURCE_ENTRY):
                thumbnails_downloaded = self._download_parent_thumbnails(
                    thumbnails_downloaded=thumbnails_downloaded,
                    thumbnail_list_info=collection_url.source_thumbnails,
                    entry=entry,
                    parent=EntryParent(
                        entry.kwargs(SOURCE_ENTRY), working_directory=self.working_directory
                    ),
                )
