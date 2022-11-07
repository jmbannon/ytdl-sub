from typing import Any
from typing import Dict

from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.downloaders.generic.url import UrlDownloadOptions
from ytdl_sub.downloaders.generic.validators import MultiUrlValidator
from ytdl_sub.validators.url_validator import YoutubeVideoUrlValidator


class YoutubeVideoDownloaderOptions(DownloaderValidator):
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

    CLI usage:

    .. code-block:: bash

       ytdl-sub dl --preset "example_preset" --youtube.video_url "youtube.com/watch?v=VMAPTo7RVDo"
    """

    _required_keys = {"video_url"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate a YouTube video source
        """
        if isinstance(value, dict):
            value["video_url"] = value.get("video_url", "youtube.com/watch?v=VMAPTo7RVDo")
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)
        self._video_url = self._validate_key("video_url", YoutubeVideoUrlValidator).video_url

    @property
    def collection_validator(self) -> MultiUrlValidator:
        """Downloads the video url"""
        return UrlDownloadOptions(
            name=self._name, value={"url": self.video_url}
        ).collection_validator

    @property
    def video_url(self) -> str:
        """
        Required. The url of the video, i.e. ``youtube.com/watch?v=VMAPTo7RVDo``.
        """
        return self._video_url


class YoutubeVideoDownloader(Downloader[YoutubeVideoDownloaderOptions]):
    downloader_options_type = YoutubeVideoDownloaderOptions

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
