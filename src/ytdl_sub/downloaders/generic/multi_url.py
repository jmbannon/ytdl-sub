from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.downloaders.generic.validators import MultiUrlValidator


class MultiUrlDownloadOptions(MultiUrlValidator, DownloaderValidator):
    """
    Downloads from multiple URLs. If an entry is returned from more than one URL, it will
    resolve to the bottom-most URL settings.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          download:
            # required
            download_strategy: "multi_url"
            urls:
              - url: "youtube.com/channel/UCsvn_Po0SmunchJYtttWpOxMg"
                variables:
                  season_index: "1"
                  season_name: "Uploads"
                playlist_thumbnails:
                  - name: "poster.jpg"
                    uid: "avatar_uncropped"
                  - name: "fanart.jpg"
                    uid: "banner_uncropped"
                  - name: "season{season_index}-poster.jpg"
                    uid: "latest_entry"
              - url: "https://www.youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg"
                variables:
                  season_index: "2"
                  season_name: "Playlist as Season"
                playlist_thumbnails:
                  - name: "season{season_index}-poster.jpg"
                    uid: "latest_entry"
    """

    @property
    def collection_validator(self) -> MultiUrlValidator:
        """Returns itself!"""
        return self


class MultiUrlDownloader(Downloader[MultiUrlDownloadOptions]):
    downloader_options_type = MultiUrlDownloadOptions
