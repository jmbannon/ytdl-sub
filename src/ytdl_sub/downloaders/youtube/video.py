from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from ytdl_sub.downloaders.youtube.abc import YoutubeDownloader
from ytdl_sub.downloaders.youtube.abc import YoutubeDownloaderOptions
from ytdl_sub.entries.youtube import YoutubeVideo
from ytdl_sub.utils.chapters import Chapters
from ytdl_sub.utils.ffmpeg import add_ffmpeg_metadata
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.validators.url_validator import YoutubeVideoUrlValidator
from ytdl_sub.validators.validators import StringValidator


class YoutubeVideoDownloaderOptions(YoutubeDownloaderOptions):
    """
    Downloads a single youtube video. This download strategy is intended for CLI usage performing
    a one-time download of a video, not a subscription.

    Usage:

    .. code-block:: yaml

      presets:
        example_preset:
          youtube:
            # required
            download_strategy: "video"
            video_url: "youtube.com/watch?v=VMAPTo7RVDo"
            # optional
            chapter_timestamps: path/to/timestamps.txt

    CLI usage:

    .. code-block:: bash

       ytdl-sub dl --preset "example_preset" --youtube.video_url "youtube.com/watch?v=VMAPTo7RVDo"
    """

    _required_keys = {"video_url"}
    _optional_keys = {"chapter_timestamps"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._video_url = self._validate_key("video_url", YoutubeVideoUrlValidator).video_url
        self._chapter_timestamps = self._validate_key_if_present(
            "chapter_timestamps", StringValidator
        )

    @property
    def video_url(self) -> str:
        """
        Required. The url of the video, i.e. ``youtube.com/watch?v=VMAPTo7RVDo``.
        """
        return self._video_url

    @property
    def chapter_timestamps(self) -> Optional[str]:
        """
        Optional. The path to the file containing the timestamps to embed into the video as
        chapters. Should be formatted as:

        .. code-block:: markdown

           0:00 Intro
           0:24 Blackwater Park
           10:23 Bleak
           16:39 Jokes
           1:02:23 Ending
        """
        if self._chapter_timestamps:
            return self._chapter_timestamps.value
        return None


class YoutubeVideoDownloader(YoutubeDownloader[YoutubeVideoDownloaderOptions, YoutubeVideo]):
    downloader_options_type = YoutubeVideoDownloaderOptions
    downloader_entry_type = YoutubeVideo

    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        Default `ytdl_options`_ for ``video``

        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
        """
        return dict(
            super().ytdl_option_defaults(),
            **{"break_on_existing": True},
        )

    def download(self) -> List[YoutubeVideo] | List[Tuple[YoutubeVideo, FileMetadata]]:
        """Download a single Youtube video"""
        entry_dict = self.extract_info(url=self.download_options.video_url)
        video = YoutubeVideo(entry_dict=entry_dict, working_directory=self.working_directory)

        # If no chapters, just return the video
        if not self.download_options.chapter_timestamps:
            return [video]

        # Otherwise, add the chapters and return the video + chapter metadata
        chapters = Chapters.from_file(chapters_file_path=self.download_options.chapter_timestamps)
        if not self.is_dry_run:
            add_ffmpeg_metadata(
                file_path=video.get_download_file_path(),
                chapters=chapters,
                file_duration_sec=video.kwargs("duration"),
            )

        file_metadata = chapters.to_file_metadata(title="Chapters embedded into the video:")

        return [(video, file_metadata)]
