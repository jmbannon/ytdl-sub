from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.downloaders.generic.collection_validator import CollectionValidator
from ytdl_sub.entries.entry import Entry


class CollectionDownloadOptions(CollectionValidator, DownloaderValidator):
    """
    Downloads from multiple URLs. If an entry is returned from more than one URL, it will
    resolve to the bottom-most URL settings.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          generic:
            # required
            download_strategy: "collection"
            urls:
            - url: "soundcloud.com/tracks"
              variables:
                season: "1"
                album: "{title}"
            - url: "soundcloud.com/albums"
              variables:
                season: "1"
                album: "{playlist_title}"
    """

    @property
    def collection_validator(self) -> CollectionValidator:
        """Returns itself!"""
        return self


class CollectionDownloader(Downloader[CollectionDownloadOptions, Entry]):
    downloader_options_type = CollectionDownloadOptions
    downloader_entry_type = Entry
