import abc
import json
import os
from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

import yt_dlp as ytdl
from yt_dlp.utils import ExistingVideoReached
from yt_dlp.utils import RejectedVideoReached

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadArchiver
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

logger = Logger.get(name="downloader")


class DownloaderValidator(StrictDictValidator, ABC):
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

    @classmethod
    def ytdl_option_overrides(cls) -> Dict:
        """Global overrides that even overwrite user input"""
        return {"writethumbnail": True, "noplaylist": True}

    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
        """
        return {"ignoreerrors": True}

    @classmethod
    def _configure_ytdl_options(
        cls,
        working_directory: str,
        ytdl_options: Optional[Dict],
    ) -> Dict:
        """Configure the ytdl options for the downloader"""
        if ytdl_options is None:
            ytdl_options = {}

        # Overwrite defaults with input
        ytdl_options = dict(cls.ytdl_option_defaults(), **ytdl_options)

        # Overwrite defaults + input with global options
        ytdl_options = dict(ytdl_options, **cls.ytdl_option_overrides())

        # Overwrite the output location with the specified working directory
        ytdl_options["outtmpl"] = str(Path(working_directory) / "%(id)s.%(ext)s")

        return ytdl_options

    def __init__(
        self,
        download_options: DownloaderOptionsT,
        enhanced_download_archive: EnhancedDownloadArchive,
        ytdl_options: Optional[Dict] = None,
    ):
        """
        Parameters
        ----------
        download_options
            Options validator for this downloader
        enhanced_download_archive
            Download archive
        ytdl_options
            YTDL options validator
        """
        DownloadArchiver.__init__(self=self, enhanced_download_archive=enhanced_download_archive)
        self.download_options = download_options
        self.ytdl_options = self._configure_ytdl_options(
            ytdl_options=ytdl_options,
            working_directory=self.working_directory,
        )

    @contextmanager
    def ytdl_downloader(self, ytdl_options_overrides: Optional[Dict] = None) -> ytdl.YoutubeDL:
        """
        Context manager to interact with yt_dlp.
        """
        ytdl_options = self.ytdl_options
        if ytdl_options_overrides is not None:
            ytdl_options = dict(ytdl_options, **ytdl_options_overrides)

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
        return self.ytdl_options.get("skip_download", False)

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

    def extract_info_via_info_json(
        self, ytdl_options_overrides: Optional[Dict] = None, **kwargs
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
        **kwargs
            arguments passed directory to YoutubeDL extract_info
        """
        if ytdl_options_overrides is None:
            ytdl_options_overrides = {}

        ytdl_options_overrides = dict(ytdl_options_overrides, **{"writeinfojson": True})

        try:
            _ = self.extract_info(ytdl_options_overrides=ytdl_options_overrides, **kwargs)
        except RejectedVideoReached:
            logger.debug("RejectedVideoReached, stopping additional downloads")
        except ExistingVideoReached:
            logger.debug("ExistingVideoReached, stopping additional downloads")

        return self._get_entry_dicts_from_info_json_files()

    @abc.abstractmethod
    def download(self) -> List[DownloaderEntryT]:
        """The function to perform the download of all media entries"""

    def post_download(self, overrides: Overrides):
        """
        After all media entries have been downloaded, post processed, and moved to the output
        directory, run this function. This lets the downloader add any extra files directly to the
        output directory, for things like YT channel image, banner.

        Parameters
        ----------
        overrides:
            Subscription overrides
        """
