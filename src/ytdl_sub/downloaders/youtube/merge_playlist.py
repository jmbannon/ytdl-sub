from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from ytdl_sub.downloaders.youtube.abc import YoutubeDownloader
from ytdl_sub.downloaders.youtube.playlist import YoutubePlaylistDownloaderOptions
from ytdl_sub.entries.youtube import YoutubeVideo
from ytdl_sub.utils.chapters import Chapters
from ytdl_sub.utils.chapters import Timestamp
from ytdl_sub.utils.ffmpeg import add_ffmpeg_metadata
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.validators.validators import BoolValidator


class YoutubeMergePlaylistDownloaderOptions(YoutubePlaylistDownloaderOptions):
    r"""
    Downloads all videos in a playlist and merges them into a single video.

    Usage:

    .. code-block:: yaml

      presets:
        example_preset:
          youtube:
            # required
            download_strategy: "merge_playlist"
            playlist_url: "https://www.youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg"
            # optional
            add_chapters: False

    CLI usage:

    .. code-block:: bash

       ytdl-sub dl \
         --preset "example_preset" \
         --youtube.playlist_url "https://www.youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg" \
         --youtube.add_chapters True
    """

    _required_keys = {"playlist_url"}
    _optional_keys = {"add_chapters"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._add_chapters = self._validate_key_if_present(
            "add_chapters", validator=BoolValidator, default=False
        ).value

    @property
    def add_chapters(self) -> Optional[bool]:
        """
        Optional. Whether to add chapters using each video's title in the merged playlist.
        Defaults to False.
        """
        return self._add_chapters


class YoutubeMergePlaylistDownloader(
    YoutubeDownloader[YoutubeMergePlaylistDownloaderOptions, YoutubeVideo]
):
    downloader_options_type = YoutubeMergePlaylistDownloaderOptions
    downloader_entry_type = YoutubeVideo
    supports_download_archive = False

    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        Default `ytdl_options`_ for ``merge_playlist``

        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
             playlistreverse: True  # Sort the playlist so it begins with the first entry
             postprocessors:
               # Convert the videos to mkv format
               - key: "FFmpegVideoConvertor"
                 when: "post_process"
                 preferedformat: "mkv"
               # Concatenate all the playlist videos into a single file
               - key: "FFmpegConcat"
                 when: "playlist"
        """
        return dict(
            super().ytdl_option_defaults(),
            **{
                "playlistreverse": True,
                "postprocessors": [
                    {
                        "key": "FFmpegVideoConvertor",
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

    def _get_chapters(self, merged_video: YoutubeVideo, add_chapters: bool) -> FileMetadata:
        titles: List[str] = []
        timestamps: List[Timestamp] = []

        current_timestamp_sec = 0
        for video_entry in merged_video.kwargs("entries"):
            timestamps.append(Timestamp(current_timestamp_sec))
            titles.append(video_entry["title"])

            current_timestamp_sec += video_entry["duration"]

        chapters = Chapters(timestamps=timestamps, titles=titles)

        if not self.is_dry_run and add_chapters:
            add_ffmpeg_metadata(
                file_path=merged_video.get_download_file_path(),
                chapters=chapters,
                file_duration_sec=merged_video.kwargs("duration"),
            )

        return chapters.to_file_metadata(title="Timestamps of playlist videos in the merged file:")

    def _to_merged_video(self, entry_dict: Dict) -> YoutubeVideo:
        """
        Adds a few entries not included in a playlist entry to make it look like a merged video
        entry_dict
        """
        # Set the upload date to be the latest playlist video date
        entry_dict["upload_date"] = max(
            playlist_entry["upload_date"] for playlist_entry in entry_dict["entries"]
        )
        entry_dict["duration"] = sum(
            playlist_entry["duration"] for playlist_entry in entry_dict["entries"]
        )
        entry_dict["ext"] = (
            entry_dict["requested_downloads"][0]["ext"]
            if "requested_downloads" in entry_dict
            else "mkv"
        )
        return YoutubeVideo(entry_dict=entry_dict, working_directory=self.working_directory)

    def download(self) -> List[Tuple[YoutubeVideo, FileMetadata]]:
        """Download a single Youtube video, then split it into multiple videos"""
        merged_video = self._to_merged_video(
            entry_dict=self.extract_info(url=self.download_options.playlist_url)
        )
        merged_video_metadata = self._get_chapters(
            merged_video=merged_video, add_chapters=self.download_options.add_chapters
        )
        return [(merged_video, merged_video_metadata)]
