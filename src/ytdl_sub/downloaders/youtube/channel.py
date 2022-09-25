from typing import Dict
from typing import Generator
from typing import List
from typing import Optional

from ytdl_sub.downloaders.generic.collection_validator import CollectionValidator
from ytdl_sub.downloaders.youtube.abc import YoutubeDownloader
from ytdl_sub.downloaders.youtube.abc import YoutubeDownloaderOptions
from ytdl_sub.entries.youtube import YoutubeVideo
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.url_validator import YoutubeChannelUrlValidator


class YoutubeChannelDownloaderOptions(YoutubeDownloaderOptions):
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
            value={"urls": [{"url": self.channel_url, "playlist_thumbnails": playlist_thumbnails}]},
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


class YoutubeChannelDownloader(YoutubeDownloader[YoutubeChannelDownloaderOptions, YoutubeVideo]):
    downloader_options_type = YoutubeChannelDownloaderOptions
    downloader_entry_type = YoutubeVideo

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

    def download(self) -> Generator[YoutubeVideo, None, None]:
        """
        Downloads all videos from a channel
        """
        for entry in super().download():
            yield entry.to_type(YoutubeVideo)
