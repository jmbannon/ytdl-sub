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
from yt_dlp.utils import MaxDownloadsReached
from yt_dlp.utils import RejectedVideoReached

from ytdl_sub.config.preset_options import AddsVariablesMixin
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.downloaders.generic.validators import MultiUrlValidator
from ytdl_sub.downloaders.generic.validators import UrlThumbnailListValidator
from ytdl_sub.downloaders.generic.validators import UrlValidator
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.entry_parent import EntryParent
from ytdl_sub.entries.variables.kwargs import COMMENTS
from ytdl_sub.entries.variables.kwargs import DOWNLOAD_INDEX
from ytdl_sub.entries.variables.kwargs import PLAYLIST_ENTRY
from ytdl_sub.entries.variables.kwargs import REQUESTED_SUBTITLES
from ytdl_sub.entries.variables.kwargs import SOURCE_ENTRY
from ytdl_sub.entries.variables.kwargs import SPONSORBLOCK_CHAPTERS
from ytdl_sub.entries.variables.kwargs import UPLOAD_DATE_INDEX
from ytdl_sub.thread.log_entries_downloaded_listener import LogEntriesDownloadedListener
from ytdl_sub.utils.exceptions import FileNotDownloadedException
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.thumbnail import ThumbnailTypes
from ytdl_sub.utils.thumbnail import convert_download_thumbnail
from ytdl_sub.utils.thumbnail import convert_url_thumbnail
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadArchiver
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

# pylint: disable=too-many-instance-attributes

download_logger = Logger.get(name="downloader")


class DownloaderValidator(StrictDictValidator, AddsVariablesMixin, ABC):
    """
    Placeholder class to define downloader options
    """

    @property
    @abc.abstractmethod
    def collection_validator(self) -> MultiUrlValidator:
        """
        Returns
        -------
        MultiUrlValidator
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


class URLDownloadState:
    def __init__(self, entries_total: int):
        self.entries_total = entries_total
        self.entries_downloaded = 0
        self.thumbnails_downloaded: Set[str] = set()


class Downloader(DownloadArchiver, Generic[DownloaderOptionsT], ABC):
    """
    Class that interacts with ytdl to perform the download of metadata and content,
    and should translate that to list of Entry objects.
    """

    downloader_options_type: Type[DownloaderValidator] = DownloaderValidator

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
        download_ytdl_options: YTDLOptionsBuilder,
        metadata_ytdl_options: YTDLOptionsBuilder,
        overrides: Overrides,
    ):
        """
        Parameters
        ----------
        download_options
            Options validator for this downloader
        enhanced_download_archive
            Download archive
        download_ytdl_options
            YTDL options builder for downloading media
        metadata_ytdl_options
            YTDL options builder for downloading metadata
        overrides
            Override variables
        """
        DownloadArchiver.__init__(self=self, enhanced_download_archive=enhanced_download_archive)
        self.download_options = download_options
        self.overrides = overrides
        self._download_ytdl_options_builder = download_ytdl_options
        self._metadata_ytdl_options_builder = metadata_ytdl_options
        self._downloaded_entries: Set[str] = set()

        self._url_state: Optional[URLDownloadState] = None

    @property
    def download_ytdl_options(self) -> Dict:
        """
        Returns
        -------
        YTLD options dict for downloading
        """
        return (
            self._download_ytdl_options_builder.clone()
            .add(self.ytdl_option_defaults(), before=True)
            .to_dict()
        )

    @property
    def metadata_ytdl_options(self) -> Dict:
        """
        Returns
        -------
        YTDL options dict for fetching metadata
        """
        return (
            self._metadata_ytdl_options_builder.clone()
            .add(self.ytdl_option_defaults(), before=True)
            .to_dict()
        )

    @classmethod
    @contextmanager
    def ytdl_downloader(cls, ytdl_options_overrides: Dict) -> ytdl.YoutubeDL:
        """
        Context manager to interact with yt_dlp.
        """
        download_logger.debug("ytdl_options: %s", str(ytdl_options_overrides))
        with Logger.handle_external_logs(name="yt-dlp"):
            # Deep copy ytdl_options in case yt-dlp modifies the dict
            with ytdl.YoutubeDL(copy.deepcopy(ytdl_options_overrides)) as ytdl_downloader:
                yield ytdl_downloader

    @property
    def is_dry_run(self) -> bool:
        """
        Returns
        -------
        True if dry-run is enabled. False otherwise.
        """
        return self.download_ytdl_options.get("skip_download", False)

    @property
    def is_entry_thumbnails_enabled(self) -> bool:
        """
        Returns
        -------
        True if entry thumbnails should be downloaded. False otherwise.
        """
        return self.download_ytdl_options.get("writethumbnail", False)

    def extract_info(self, ytdl_options_overrides: Dict, **kwargs) -> Dict:
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
        ytdl_options_overrides: Dict,
        is_downloaded_fn: Optional[Callable[[], bool]] = None,
        is_thumbnail_downloaded_fn: Optional[Callable[[], bool]] = None,
        **kwargs,
    ) -> Dict:
        """
        Wrapper around yt_dlp.YoutubeDL.YoutubeDL.extract_info
        All kwargs will passed to the extract_info function.

        This should be used when downloading a single entry. Checks if the entry's video
        and thumbnail files exist - retry if they do not.

        Parameters
        ----------
        ytdl_options_overrides
            Dict containing ytdl args to override other predefined ytdl args
        is_downloaded_fn
            Optional. Function to check if the entry is downloaded
        is_thumbnail_downloaded_fn
            Optional. Function to check if the entry thumbnail is downloaded
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

            is_downloaded = is_downloaded_fn is None or is_downloaded_fn()
            is_thumbnail_downloaded = (
                is_thumbnail_downloaded_fn is None or is_thumbnail_downloaded_fn()
            )

            if is_downloaded and is_thumbnail_downloaded:
                return entry_dict

            # If the video file is downloaded but the thumbnail is not, then do not download
            # the video again
            if is_downloaded and not is_thumbnail_downloaded:
                copied_ytdl_options_overrides["skip_download"] = True
                copied_ytdl_options_overrides["writethumbnail"] = True

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
        ytdl_options_overrides: Dict,
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
            Dict containing ytdl args to override other predefined ytdl args
        log_prefix_on_info_json_dl
            Optional. Spin a new thread to listen for new info.json files. Log
            f'{log_prefix_on_info_json_dl} {title}' when a new one appears
        **kwargs
            arguments passed directory to YoutubeDL extract_info
        """
        try:
            with self._listen_and_log_downloaded_info_json(log_prefix=log_prefix_on_info_json_dl):
                _ = self.extract_info(ytdl_options_overrides=ytdl_options_overrides, **kwargs)
        except RejectedVideoReached:
            download_logger.info(
                "RejectedVideoReached, stopping additional downloads. "
                "Disable by setting `ytdl_options.break_on_reject` to False."
            )
        except ExistingVideoReached:
            download_logger.info(
                "ExistingVideoReached, stopping additional downloads. "
                "Disable by setting `ytdl_options.break_on_existing` to False."
            )
        except MaxDownloadsReached:
            download_logger.info("MaxDownloadsReached, stopping additional downloads.")

        return self._get_entry_dicts_from_info_json_files()

    ###############################################################################################
    # DOWNLOAD FUNCTIONS

    def _is_downloaded(self, entry: Entry) -> bool:
        return entry.ytdl_uid() in self._downloaded_entries

    def _mark_downloaded(self, entry: Entry) -> None:
        self._downloaded_entries.add(entry.ytdl_uid())

    @property
    def collection(self) -> MultiUrlValidator:
        """Return the download options collection"""
        return self.download_options.collection_validator

    @contextlib.contextmanager
    def _separate_download_archives(self, clear_info_json_files: bool = False):
        """
        Separate download archive writing between collection urls. This is so break_on_existing
        does not break when downloading from subset urls.

        Parameters
        ----------
        clear_info_json_files
            Whether to delete info.json files after yield
        """
        archive_path = self.download_ytdl_options.get("download_archive", "")
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
            FileHandler.move(src_file_path=backup_archive_path, dst_file_path=archive_path)

        # Clear info json files if true
        if clear_info_json_files:
            info_json_files = [
                Path(self.working_directory) / path
                for path in os.listdir(self.working_directory)
                if path.endswith(".info.json")
            ]
            for info_json_file in info_json_files:
                FileHandler.delete(info_json_file)

    def _extract_entry_info_with_retry(self, entry: Entry) -> Entry:
        download_entry_dict = self.extract_info_with_retry(
            is_downloaded_fn=None if self.is_dry_run else entry.is_downloaded,
            is_thumbnail_downloaded_fn=None
            if (self.is_dry_run or not self.is_entry_thumbnails_enabled)
            else entry.is_thumbnail_downloaded,
            url=entry.webpage_url,
            ytdl_options_overrides=self.download_ytdl_options,
        )
        return Entry(download_entry_dict, working_directory=self.working_directory)

    def _download_entry(self, entry: Entry) -> Entry:
        download_entry = self._extract_entry_info_with_retry(entry=entry)

        upload_date_idx = self._enhanced_download_archive.mapping.get_num_entries_with_upload_date(
            upload_date_standardized=entry.upload_date_standardized
        )
        download_idx = self._enhanced_download_archive.mapping.get_num_entries()

        entry.add_kwargs(
            {
                # Subtitles are not downloaded in metadata run, only here, so move over
                REQUESTED_SUBTITLES: download_entry.kwargs_get(REQUESTED_SUBTITLES),
                # Same with sponsorblock chapters
                SPONSORBLOCK_CHAPTERS: download_entry.kwargs_get(SPONSORBLOCK_CHAPTERS),
                COMMENTS: download_entry.kwargs_get(COMMENTS),
                # Tracks number of entries downloaded
                DOWNLOAD_INDEX: download_idx,
                # Tracks number of entries with the same upload date to make them unique
                UPLOAD_DATE_INDEX: upload_date_idx,
            }
        )

        return entry

    def _download_entries(self, entries: List[Entry]) -> Generator[Entry, None, None]:
        # Download entries in reverse order since they are scraped in the opposite direction.
        # Helps deal with break_on_existing
        for entry in reversed(entries):
            self._url_state.entries_downloaded += 1

            if self._is_downloaded(entry):
                download_logger.info(
                    "Already downloaded entry %d/%d: %s",
                    self._url_state.entries_downloaded,
                    self._url_state.entries_total,
                    entry.title,
                )
                continue

            download_logger.info(
                "Downloading entry %d/%d: %s",
                self._url_state.entries_downloaded,
                self._url_state.entries_total,
                entry.title,
            )
            yield self._download_entry(entry)
            self._mark_downloaded(entry)

    def _download_parent_entry(self, parent: EntryParent) -> Generator[Entry, None, None]:
        for entry_child in self._download_entries(parent.entry_children()):
            yield entry_child

        # Recursion the parent's parent entries
        for parent_child in reversed(parent.parent_children()):
            for entry_child in self._download_parent_entry(parent=parent_child):
                yield entry_child

    def _set_collection_variables(self, collection_url: UrlValidator, entry: Entry | EntryParent):
        if isinstance(entry, EntryParent):
            for child in entry.parent_children():
                self._set_collection_variables(collection_url, child)
            for child in entry.entry_children():
                child.add_variables(
                    variables_to_add=collection_url.variables.dict_with_format_strings
                )

        elif isinstance(entry, Entry):
            entry.add_variables(variables_to_add=collection_url.variables.dict_with_format_strings)

    def _download_url_metadata(
        self, collection_url: UrlValidator
    ) -> Tuple[List[EntryParent], List[Entry]]:
        """
        Downloads only info.json files and forms EntryParent trees
        """
        url = self.overrides.apply_formatter(collection_url.url)

        with self._separate_download_archives():
            entry_dicts = self.extract_info_via_info_json(
                ytdl_options_overrides=self.metadata_ytdl_options,
                url=url,
                log_prefix_on_info_json_dl="Downloading metadata for",
            )

        parents = EntryParent.from_entry_dicts(
            url=url,
            entry_dicts=entry_dicts,
            working_directory=self.working_directory,
        )
        orphans = EntryParent.from_entry_dicts_with_no_parents(
            parents=parents, entry_dicts=entry_dicts, working_directory=self.working_directory
        )

        for parent_entry in parents:
            self._set_collection_variables(collection_url, parent_entry)
        for entry in orphans:
            self._set_collection_variables(collection_url, entry)

        return parents, orphans

    def _download(
        self,
        parents: List[EntryParent],
        orphans: List[Entry],
    ) -> Generator[Entry, None, None]:
        """
        Downloads the leaf entries from EntryParent trees
        """
        # Delete info json files afterwards so other collection URLs do not use them
        with self._separate_download_archives(clear_info_json_files=True):
            for parent in parents:
                for entry_child in self._download_parent_entry(parent=parent):
                    yield entry_child

            for orphan in self._download_entries(orphans):
                yield orphan

    def download(
        self,
    ) -> Iterable[Entry] | Iterable[Tuple[Entry, FileMetadata]]:
        """The function to perform the download of all media entries"""
        # download the bottom-most urls first since they are top-priority
        for collection_url in reversed(self.collection.urls.list):
            parents, orphan_entries = self._download_url_metadata(collection_url=collection_url)

            # TODO: Encapsulate this logic into its own class
            self._url_state = URLDownloadState(
                entries_total=sum(parent.num_children() for parent in parents) + len(orphan_entries)
            )

            download_logger.info(
                "Beginning downloads for %s", self.overrides.apply_formatter(collection_url.url)
            )
            for entry in self._download(parents=parents, orphans=orphan_entries):
                # Update thumbnails in case of last_entry
                self._download_url_thumbnails(collection_url=collection_url, entry=entry)
                yield entry

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
        thumbnail_list_info: UrlThumbnailListValidator,
        entry: Entry,
        parent: EntryParent,
    ) -> None:
        """
        Downloads and moves channel avatar and banner images to the output directory.
        """
        for thumbnail_info in thumbnail_list_info.list:
            thumbnail_name = self.overrides.apply_formatter(thumbnail_info.name, entry=entry)
            thumbnail_id = self.overrides.apply_formatter(thumbnail_info.uid)

            # If latest entry, always update the thumbnail on each entry
            if thumbnail_id == ThumbnailTypes.LATEST_ENTRY:
                # Make sure the entry's thumbnail is converted to jpg
                convert_download_thumbnail(entry, error_if_not_found=False)

                # always save in dry-run even if it doesn't exist...
                if self.is_dry_run or os.path.isfile(entry.get_download_thumbnail_path()):
                    self.save_file(
                        file_name=entry.get_download_thumbnail_name(),
                        output_file_name=thumbnail_name,
                        copy_file=True,
                    )
                    self._url_state.thumbnails_downloaded.add(thumbnail_name)
                continue

            # If not latest entry and the thumbnail has already been downloaded, then skip
            if thumbnail_name in self._url_state.thumbnails_downloaded:
                continue

            if (thumbnail_url := parent.get_thumbnail_url(thumbnail_id=thumbnail_id)) is None:
                download_logger.debug("Failed to find thumbnail id '%s'", thumbnail_id)
                continue

            if self._download_thumbnail(
                thumbnail_url=thumbnail_url,
                output_thumbnail_path=str(Path(self.working_directory) / thumbnail_name),
            ):
                self.save_file(file_name=thumbnail_name)
                self._url_state.thumbnails_downloaded.add(thumbnail_name)
            else:
                download_logger.debug("Failed to download thumbnail id '%s'", thumbnail_id)

    def _download_url_thumbnails(self, collection_url: UrlValidator, entry: Entry):
        """
        After all media entries have been downloaded, post processed, and moved to the output
        directory, run this function. This lets the downloader add any extra files directly to the
        output directory, for things like YT channel image, banner.
        """
        if entry.kwargs_contains(PLAYLIST_ENTRY):
            self._download_parent_thumbnails(
                thumbnail_list_info=collection_url.playlist_thumbnails,
                entry=entry,
                parent=EntryParent(
                    entry.kwargs(PLAYLIST_ENTRY), working_directory=self.working_directory
                ),
            )

        if entry.kwargs_contains(SOURCE_ENTRY):
            self._download_parent_thumbnails(
                thumbnail_list_info=collection_url.source_thumbnails,
                entry=entry,
                parent=EntryParent(
                    entry.kwargs(SOURCE_ENTRY), working_directory=self.working_directory
                ),
            )
