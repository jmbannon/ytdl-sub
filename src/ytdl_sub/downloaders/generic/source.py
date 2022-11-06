from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.downloaders.generic.collection_validator import CollectionUrlValidator
from ytdl_sub.downloaders.generic.collection_validator import CollectionValidator


class SourceDownloadOptions(CollectionUrlValidator, DownloaderValidator):
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
    """

    @property
    def collection_validator(self) -> CollectionValidator:
        """Returns itself!"""
        return CollectionValidator(
            name=self._name,
            value={"urls": [self._value]},
        )


class SourceDownloader(Downloader[SourceDownloadOptions]):
    downloader_options_type = SourceDownloadOptions
