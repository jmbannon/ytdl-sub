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
from typing import Tuple
from typing import Type
from typing import TypeVar

import yt_dlp as ytdl
from yt_dlp.utils import ExistingVideoReached
from yt_dlp.utils import RejectedVideoReached

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.entry import Entry
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator


class DownloaderValidator(StrictDictValidator, ABC):
    """
    Placeholder class to define downloader options
    """


DownloaderOptionsT = TypeVar("DownloaderOptionsT", bound=DownloaderValidator)
DownloaderEntryT = TypeVar("DownloaderEntryT", bound=Entry)
DownloaderParentEntryT = TypeVar("DownloaderParentEntryT", bound=BaseEntry)


class Downloader(Generic[DownloaderOptionsT, DownloaderEntryT], ABC):
    """
    Class that interacts with ytdl to perform the download of metadata and content,
    and should translate that to list of Entry objects.
    """

    downloader_options_type: Type[DownloaderValidator] = DownloaderValidator
    downloader_entry_type: Type[Entry] = Entry

    @classmethod
    def ytdl_option_overrides(cls) -> Dict:
        """Global overrides that even overwrite user input"""
        return {"writethumbnail": True, "noplaylist": True}

    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """Downloader defaults that can be overwritten from user input"""
        return {}

    @classmethod
    def _configure_ytdl_options(
        cls,
        working_directory: str,
        ytdl_options: Optional[Dict],
        download_archive_file_name: Optional[str],
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

        # If a download archive file name is provided, set it to that
        ytdl_options["download_archive"] = str(Path(working_directory) / download_archive_file_name)

        return ytdl_options

    def __init__(
        self,
        working_directory: str,
        download_options: DownloaderOptionsT,
        ytdl_options: Optional[Dict] = None,
        download_archive_file_name: Optional[str] = None,
    ):
        """
        Parameters
        ----------
        working_directory
            Path to the working directory
        download_options
            Options validator for this downloader
        ytdl_options
            YTDL options validator
        download_archive_file_name
            Optional. Name of the download archive file that should reside in the working directory
        """
        self.working_directory = working_directory
        self.download_options = download_options
        self.ytdl_options = Downloader._configure_ytdl_options(
            ytdl_options=ytdl_options,
            working_directory=self.working_directory,
            download_archive_file_name=download_archive_file_name,
        )

    @contextmanager
    def ytdl_downloader(self, ytdl_options_overrides: Optional[Dict] = None) -> ytdl.YoutubeDL:
        """
        Context manager to interact with yt_dlp.
        """
        ytdl_options = self.ytdl_options
        if ytdl_options_overrides is not None:
            ytdl_options = dict(ytdl_options, **ytdl_options_overrides)

        with ytdl.YoutubeDL(ytdl_options) as ytdl_downloader:
            yield ytdl_downloader

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

    def extract_info_json(self, ytdl_options_overrides: Optional[Dict] = None, **kwargs) -> None:
        """
        Wrapper around yt_dlp.YoutubeDL.YoutubeDL.extract_info

        All kwargs will passed to the extract_info function. This also enables ytdl to write
        .info.json files for all media downloaded.

        Catches RejectedVideoReached and ExistingVideoReached exceptions.

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
        except (RejectedVideoReached, ExistingVideoReached):
            pass

    def extract_from_info_json(
        self, parent_prefix: str, parent_entry_type: Type[DownloaderParentEntryT]
    ) -> Tuple[DownloaderParentEntryT, List[DownloaderEntryT]]:
        """
        Reads all .info.json files in the working directory, and casts them to the
        parent_entry_type (i.e. YoutubeChannel) and downloader_entry_type (i.e. YoutubeVideo)

        Parameters
        ----------
        parent_prefix
            info.json file name prefix to indicate its the parent (i.e. the YT channel id)
        parent_entry_type
            Class type for the parent entry

        Returns
        -------
        Tuple containing parent, list of videos belong to the parent
        """
        # Load the entries from info.json

        parent_entry: Optional[DownloaderParentEntryT] = None
        entries: List[DownloaderEntryT] = []

        for file_name in os.listdir(self.working_directory):
            if file_name.endswith(".info.json"):
                with open(Path(self.working_directory) / file_name, "r", encoding="utf-8") as file:

                    if file_name.startswith(parent_prefix):
                        parent_entry = parent_entry_type(
                            entry_dict=json.load(file), working_directory=self.working_directory
                        )
                    else:
                        entries.append(
                            self.downloader_entry_type(
                                entry_dict=json.load(file), working_directory=self.working_directory
                            )
                        )

        return parent_entry, entries

    @abc.abstractmethod
    def download(self) -> List[DownloaderEntryT]:
        """The function to perform the download of all media entries"""

    def post_download(self, overrides: Overrides, output_directory: str):
        """
        After all media entries have been downloaded, post processed, and moved to the output
        directory, run this function. This lets the downloader add any extra files directly to the
        output directory, for things like YT channel image, banner.

        This ideally should not perform  any extra downloads, but rather, use the content already
        downloaded in the working directory and use it in the output directory.

        Parameters
        ----------
        overrides:
            Subscription overrides
        output_directory:
            Output directory to potentially store extra files downloaded
        """
