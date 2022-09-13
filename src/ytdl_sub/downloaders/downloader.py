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
from typing import Generic
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar

import yt_dlp as ytdl
from yt_dlp.utils import ExistingVideoReached
from yt_dlp.utils import RejectedVideoReached

from ytdl_sub.config.preset_options import AddsVariablesMixin
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.entry import Entry
from ytdl_sub.thread.log_entries_downloaded_listener import LogEntriesDownloadedListener
from ytdl_sub.utils.exceptions import FileNotDownloadedException
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadArchiver
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

download_logger = Logger.get(name="downloader")


class DownloaderValidator(StrictDictValidator, AddsVariablesMixin, ABC):
    """
    Placeholder class to define downloader options
    """


DownloaderOptionsT = TypeVar("DownloaderOptionsT", bound=DownloaderValidator)
DownloaderEntryT = TypeVar("DownloaderEntryT", bound=Entry)
DownloaderParentEntryT = TypeVar("DownloaderParentEntryT", bound=BaseEntry)


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

    @classmethod
    def added_override_variables(cls) -> List[str]:
        """
        Returns
        -------
        List of override variables that this downloader adds
        """
        return []

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

    def _filter_entry_dicts(
        self,
        entry_dicts: List[Dict],
        extractor: Optional[str] = None,
        sort_by: Optional[str] = None,
    ) -> List[Dict]:
        """
        Parameters
        ----------
        entry_dicts
            entry dicts to filter
        extractor
            Optional. Extractor that the entry dicts must have. If None, defaults to the
            entry type's extractor
        sort_by
            Optional. Sort the entry dicts on this key

        Returns
        -------
        filtered entry dicts
        """
        if extractor is None:
            extractor = self.downloader_entry_type.entry_extractor

        output = [
            entry_dict for entry_dict in entry_dicts if entry_dict.get("extractor") == extractor
        ]
        if sort_by:
            output = sorted(output, key=lambda entry_dict: entry_dict[sort_by])
        return output

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
            info_json_extractor=self.downloader_entry_type.entry_extractor,
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

    @abc.abstractmethod
    def download(
        self,
    ) -> Iterable[DownloaderEntryT] | Iterable[Tuple[DownloaderEntryT, FileMetadata]]:
        """The function to perform the download of all media entries"""

    def post_download(self):
        """
        After all media entries have been downloaded, post processed, and moved to the output
        directory, run this function. This lets the downloader add any extra files directly to the
        output directory, for things like YT channel image, banner.
        """
