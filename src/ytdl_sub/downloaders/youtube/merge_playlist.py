import copy
import os.path
import re
from pathlib import Path
from shutil import copyfile
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

from ytdl_sub.downloaders.youtube_downloader import YoutubeDownloader
from ytdl_sub.downloaders.youtube_downloader import YoutubePlaylistDownloaderOptions
from ytdl_sub.downloaders.youtube_downloader import YoutubeVideoDownloaderOptions
from ytdl_sub.entries.youtube import YoutubePlaylistVideo
from ytdl_sub.entries.youtube import YoutubeVideo
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.thumbnail import convert_download_thumbnail
from ytdl_sub.validators.validators import BoolValidator
from ytdl_sub.validators.validators import StringValidator

###############################################################################
# Youtube split video downloader + options


class YoutubeMergePlaylistDownloaderOptions(YoutubePlaylistDownloaderOptions):
    """
    Downloads all videos in a playlist and merges them into a single video.

    Usage:

    .. code-block:: yaml

      presets:
        example_preset:
          youtube:
            # required
            download_strategy: "merge_playlist"
            playlist_url: "TODO"
            # optional
            add_chapters: False

    CLI usage:

    .. code-block:: bash

       ytdl-sub dl \
         --preset "example_preset" \
         --youtube.video_url "youtube.com/watch?v=VMAPTo7RVDo" \
         --youtube.split_timestamps "path/to/timestamps.txt"

    ``split_timestamps`` file format:

    .. code-block:: markdown

       0:00 Intro
       0:24 Blackwater Park
       10:23 Bleak
       16:39 Jokes
       1:02:23 Ending

    The above will create 5 videos in total. The first timestamp must start with ``0:00``
    and the last timestamp, in this example, would create a video starting at ``1:02:23`` and
    end at Youtube video's ending.
    """

    _required_keys = {"playlist_url"}
    _optional_keys = {"add_chapters"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._add_chapters = self._validate_key_if_present(
            "add_chapters", validator=BoolValidator, default=False
        ).value

    @property
    def add_chapters(self) -> bool:
        """
        Whether to add chapters using each video's title in the merged playlist. Defaults to false.
        """
        return self._add_chapters


class YoutubeMergePlaylistDownloader(
    YoutubeDownloader[YoutubeMergePlaylistDownloaderOptions, YoutubeVideo]
):
    downloader_options_type = YoutubeMergePlaylistDownloaderOptions
    downloader_entry_type = YoutubeVideo

    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        Default `ytdl_options`_ for ``split_video``

        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
        """
        return dict(
            super().ytdl_option_defaults(),
            **{
                "playlistreverse": True,
                "postprocessors": [
                    {
                        "key": "FFmpegVideoRemuxer",
                        "when": "post_process",
                        "preferedformat": "mkv",
                    },
                    {
                        "key": "FFmpegConcat",
                        "when": "playlist",
                    },
                ],
            },
        )

    def download(self) -> List[YoutubeVideo]:
        """Download a single Youtube video, then split it into multiple videos"""
        entry_dict = self.extract_info(url=self.download_options.playlist_url)

        if self.download_options.add_chapters:
            raise NotImplemented("TODO")

        return [YoutubeVideo(entry_dict=entry_dict, working_directory=self.working_directory)]
