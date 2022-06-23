import copy
import os.path
import re
from pathlib import Path
from shutil import copyfile
from typing import Dict
from typing import List
from typing import Tuple

from ytdl_sub.downloaders.youtube_downloader import YoutubeDownloader
from ytdl_sub.downloaders.youtube_downloader import YoutubeVideoDownloaderOptions
from ytdl_sub.entries.youtube import YoutubePlaylistVideo
from ytdl_sub.entries.youtube import YoutubeVideo
from ytdl_sub.utils.chapters import Chapters
from ytdl_sub.utils.chapters import Timestamp
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.thumbnail import convert_download_thumbnail
from ytdl_sub.validators.validators import StringValidator

# Captures the following formats:
# 0:00 title
# 00:00 title
# 1:00:00 title
# 01:00:00 title
# where capture group 1 and 2 are the timestamp and title, respectively
_SPLIT_TIMESTAMP_REGEX = re.compile(r"^((?:\d\d:)?(?:\d:)?(?:\d)?\d:\d\d) (.+)$")


def _split_video_uid(source_uid: str, idx: int) -> str:
    return f"{source_uid}___{idx}"


def _split_video_ffmpeg_cmd(
    input_file: str, output_file: str, timestamps: List[Timestamp], idx: int
) -> List[str]:
    timestamp_begin = timestamps[idx].timestamp_str
    timestamp_end = timestamps[idx + 1].timestamp_str if idx + 1 < len(timestamps) else ""

    cmd = ["-i", input_file, "-ss", timestamp_begin]
    if timestamp_end:
        cmd += ["-to", timestamp_end]
    cmd += ["-vcodec", "copy", "-acodec", "copy", output_file]
    return cmd


###############################################################################
# Youtube split video downloader + options


class YoutubeSplitVideoDownloaderOptions(YoutubeVideoDownloaderOptions):
    """
    Downloads a single youtube video, then splits in to separate videos using a file containing
    timestamps. Each separate video will be formatted as if it was downloaded from a playlist.
    This download strategy is intended for CLI usage performing a one-time download of a video,
    not a subscription.

    Usage:

    .. code-block:: yaml

      presets:
        example_preset:
          youtube:
            # required
            download_strategy: "split_video"
            video_url: "youtube.com/watch?v=VMAPTo7RVDo"
            split_timestamps: path/to/timestamps.txt


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

    _required_keys = {"video_url", "split_timestamps"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._split_timestamps = self._validate_key("split_timestamps", StringValidator).value

    @property
    def split_timestamps(self) -> str:
        """
        Required. The path to the file containing the split timestamps.
        """
        return self._split_timestamps


class YoutubeSplitVideoDownloader(
    YoutubeDownloader[YoutubeSplitVideoDownloaderOptions, YoutubePlaylistVideo]
):
    downloader_options_type = YoutubeSplitVideoDownloaderOptions
    downloader_entry_type = YoutubePlaylistVideo

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
            **{"break_on_existing": True},
        )

    def _create_split_video_entry(
        self, source_entry_dict: Dict, title: str, idx: int, split_video_count: int
    ) -> YoutubePlaylistVideo:
        """
        Runs ffmpeg to create the split video
        """
        entry_dict = copy.deepcopy(source_entry_dict)
        entry_dict["title"] = title
        entry_dict["playlist_index"] = idx + 1
        entry_dict["playlist_count"] = split_video_count
        entry_dict["id"] = _split_video_uid(source_uid=entry_dict["id"], idx=idx)

        # Remove track and artist since its now split
        del entry_dict["track"]
        del entry_dict["artist"]

        return YoutubePlaylistVideo(entry_dict=entry_dict, working_directory=self.working_directory)

    def download(self) -> List[YoutubePlaylistVideo]:
        """Download a single Youtube video, then split it into multiple videos"""
        split_videos: List[YoutubePlaylistVideo] = []

        chapters = Chapters.from_file(chapters_file_path=self.download_options.split_timestamps)
        entry_dict = self.extract_info(url=self.download_options.video_url)

        entry = YoutubeVideo(entry_dict=entry_dict, working_directory=self.working_directory)
        # convert the entry thumbnail early so we do not have to guess the thumbnail extension
        # when copying it
        convert_download_thumbnail(entry=entry)

        for idx, title in enumerate(chapters.titles):
            new_uid = _split_video_uid(source_uid=entry.uid, idx=idx)

            # Get the input/output file paths
            input_file = entry.get_download_file_path()
            output_file = str(Path(self.working_directory) / f"{new_uid}.{entry.ext}")
            output_thumbnail_file = str(
                Path(self.working_directory) / f"{new_uid}.{entry.thumbnail_ext}"
            )

            # Run ffmpeg to create the split the video
            FFMPEG.run(
                _split_video_ffmpeg_cmd(
                    input_file=input_file,
                    output_file=output_file,
                    timestamps=chapters.timestamps,
                    idx=idx,
                )
            )
            # Copy the thumbnail
            copyfile(src=entry.get_download_thumbnail_path(), dst=output_thumbnail_file)

            # Format the split video as a YoutubePlaylistVideo
            split_videos.append(
                self._create_split_video_entry(
                    source_entry_dict=entry_dict,
                    title=title,
                    idx=idx,
                    split_video_count=len(chapters.timestamps),
                )
            )

        return split_videos
