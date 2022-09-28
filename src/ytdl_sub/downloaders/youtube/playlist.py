from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.downloaders.generic.collection_validator import CollectionValidator
from ytdl_sub.utils.thumbnail import ThumbnailTypes
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.url_validator import YoutubePlaylistUrlValidator


class YoutubePlaylistDownloaderOptions(DownloaderValidator):
    """
    Downloads all videos from a youtube playlist.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          youtube:
            # required
            download_strategy: "playlist"
            playlist_url: "https://www.youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg"
    """

    _required_keys = {"playlist_url"}
    _optional_keys = {"playlist_thumbnail_name"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._playlist_url = self._validate_key(
            "playlist_url", YoutubePlaylistUrlValidator
        ).playlist_url
        self._playlist_thumbnail_name = self._validate_key_if_present(
            "playlist_thumbnail_name", OverridesStringFormatterValidator
        )

    @property
    def collection_validator(self) -> CollectionValidator:
        """Downloads the playlist url"""
        playlist_thumbnails: List[Dict] = []
        if self.playlist_thumbnail_path:
            playlist_thumbnails.append(
                {
                    "name": self.playlist_thumbnail_path.format_string,
                    "uid": ThumbnailTypes.LATEST_ENTRY,
                }
            )

        return CollectionValidator(
            name=self._name,
            value={
                "urls": [
                    {
                        "url": self.playlist_url,
                        "playlist_thumbnails": playlist_thumbnails,
                        "variables": {"playlist_size": "{playlist_count}"},
                    }
                ]
            },
        )

    @property
    def playlist_url(self) -> str:
        """
        Required. The playlist's url, i.e.
        ``https://www.youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg``.
        """
        return self._playlist_url

    @property
    def playlist_thumbnail_path(self) -> Optional[OverridesStringFormatterValidator]:
        """
        Optional. Path to store the playlist's thumbnail
        """
        return self._playlist_thumbnail_name


class YoutubePlaylistDownloader(Downloader[YoutubePlaylistDownloaderOptions]):
    downloader_options_type = YoutubePlaylistDownloaderOptions

    # pylint: disable=line-too-long
    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        Default `ytdl_options`_ for ``playlist``

        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
             break_on_existing: True  # stop downloads (newest to oldest) if a video is already downloaded
        """
        return dict(
            super().ytdl_option_defaults(),
            **{"break_on_existing": True},
        )

    # pylint: enable=line-too-long
