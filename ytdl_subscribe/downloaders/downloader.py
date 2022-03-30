import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Dict
from typing import Optional

import yt_dlp as ytdl


class Downloader:
    """
    Class that interacts with ytdl to perform the download of metadata and content, and should translate that to
    list of Entry objects.
    """

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
        cls, ytdl_options: Optional[Dict], working_directory: str
    ) -> Dict:
        """Configure the ytdl options for the downloader"""
        if ytdl_options is None:
            ytdl_options = dict()

        # Overwrite defaults with input
        ytdl_options = dict(cls.ytdl_option_defaults(), **ytdl_options)

        # Overwrite defaults + input with global options
        ytdl_options = dict(ytdl_options, **cls.ytdl_option_overrides())

        # Finally overwrite the output location with the specified working directory
        ytdl_options["outtmpl"] = str(Path(working_directory) / "%(id)s.%(ext)s")
        return ytdl_options

    def __init__(
        self,
        output_directory: str,
        working_directory: Optional[str] = None,
        ytdl_options: Optional[Dict] = None,
    ):
        self.output_path = output_directory

        self.working_directory = working_directory
        if self.working_directory is None:
            self.working_directory = tempfile.TemporaryDirectory().name

        self.ytdl_options = Downloader._configure_ytdl_options(
            ytdl_options=ytdl_options,
            working_directory=self.working_directory,
        )

    @contextmanager
    def ytdl_downloader(
        self, ytdl_options_overrides: Optional[Dict] = None
    ) -> ytdl.YoutubeDL:
        """
        Context manager to interact with yt_dlp.
        """
        ytdl_options = self.ytdl_options
        if ytdl_options_overrides is not None:
            ytdl_options = dict(ytdl_options, **ytdl_options_overrides)

        with ytdl.YoutubeDL(ytdl_options) as ytdl_downloader:
            yield ytdl_downloader

    def extract_info(
        self, ytdl_options_overrides: Optional[Dict] = None, **kwargs
    ) -> Dict:
        """
        Wrapper around yt_dlp.YoutubeDL.YoutubeDL.extract_info
        All kwargs will passed to the extract_info function.
        """
        with self.ytdl_downloader(ytdl_options_overrides) as ytdl_downloader:
            return ytdl_downloader.extract_info(**kwargs)
