from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.downloaders.generic.collection_validator import CollectionValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.url_validator import YoutubeChannelUrlValidator


class YoutubeChannelDownloaderOptions(DownloaderValidator):
    """
    Downloads all videos from a youtube channel.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          youtube:
            # required
            download_strategy: "channel"
            channel_url: "UCsvn_Po0SmunchJYtttWpOxMg"
            # optional
            channel_avatar_path: "poster.jpg"
            channel_banner_path: "fanart.jpg"
    """

    _required_keys = {"channel_url"}
    _optional_keys = {
        "channel_avatar_path",
        "channel_banner_path",
    }

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate a YouTube channel source
        """
        if isinstance(value, dict):
            value["channel_url"] = value.get(
                "channel_url", "https://www.youtube.com/c/ProjectZombie603"
            )
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)
        self._channel_url = self._validate_key(
            "channel_url", YoutubeChannelUrlValidator
        ).channel_url
        self._channel_avatar_path = self._validate_key_if_present(
            "channel_avatar_path", OverridesStringFormatterValidator
        )
        self._channel_banner_path = self._validate_key_if_present(
            "channel_banner_path", OverridesStringFormatterValidator
        )

    @property
    def collection_validator(self) -> CollectionValidator:
        """Download from the channel url"""
        playlist_thumbnails: List[Dict] = []
        if self._channel_avatar_path:
            playlist_thumbnails.append(
                {
                    "name": self._channel_avatar_path.format_string,
                    "uid": "avatar_uncropped",
                }
            )
        if self._channel_banner_path:
            playlist_thumbnails.append(
                {
                    "name": self._channel_banner_path.format_string,
                    "uid": "banner_uncropped",
                }
            )

        return CollectionValidator(
            name=self._name,
            value={
                "urls": [
                    {
                        "url": self.channel_url,
                        "playlist_thumbnails": playlist_thumbnails,
                        "variables": {"playlist_size": "{playlist_count}"},
                    }
                ]
            },
        )

    @property
    def channel_url(self) -> str:
        """
        Required. The channel's url, i.e.
        ``https://www.youtube.com/channel/UCsvn_Po0SmunchJYOWpOxMg``. URLs with ``/username`` or
        ``/c`` are valid to use.
        """
        return self._channel_url

    @property
    def channel_avatar_path(self) -> Optional[OverridesStringFormatterValidator]:
        """
        Optional. Path to store the channel's avatar thumbnail image to.
        """
        return self._channel_avatar_path

    @property
    def channel_banner_path(self) -> Optional[OverridesStringFormatterValidator]:
        """
        Optional. Path to store the channel's banner image to.
        """
        return self._channel_banner_path


class YoutubeChannelDownloader(Downloader[YoutubeChannelDownloaderOptions]):
    downloader_options_type = YoutubeChannelDownloaderOptions

    # pylint: disable=line-too-long
    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        Default `ytdl_options`_ for ``channel``

        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
             break_on_existing: True  # stop downloads (newest to oldest) if a video is already downloaded
        """
        return dict(
            super().ytdl_option_defaults(),
            **{
                "break_on_existing": True,
            },
        )

    # pylint: enable=line-too-long
