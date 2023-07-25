from ytdl_sub.downloaders.url.downloader import BaseUrlDownloader
from ytdl_sub.downloaders.url.multi_url_source_options_validator import (
    MultiUrlSourceOptionsValidator,
)
from ytdl_sub.downloaders.url.validators import MultiUrlValidator
from ytdl_sub.downloaders.url.validators import UrlValidator


class UrlDownloadOptions(UrlValidator, MultiUrlSourceOptionsValidator):
    """
    Downloads from a single URL supported by yt-dlp.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          download:
            # required
            download_strategy: "url"
            url: "youtube.com/channel/UCsvn_Po0SmunchJYtttWpOxMg"
            # optional
            playlist_thumbnails:
              - name: "poster.jpg"
                uid: "avatar_uncropped"
              - name: "fanart.jpg"
                uid: "banner_uncropped"
            download_reverse: True
    """

    @property
    def collection_validator(self) -> MultiUrlValidator:
        """Returns itself!"""
        return MultiUrlValidator(
            name=self._name,
            value={"urls": [self._value]},
        )


class UrlDownloader(BaseUrlDownloader[UrlDownloadOptions]):
    plugin_options_type = UrlDownloadOptions
