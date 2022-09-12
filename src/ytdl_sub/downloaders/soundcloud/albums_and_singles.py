from typing import Dict
from typing import Generator

from ytdl_sub.downloaders.generic.collection import CollectionDownloader
from ytdl_sub.downloaders.generic.collection import CollectionDownloadOptions
from ytdl_sub.downloaders.soundcloud.abc import SoundcloudDownloader
from ytdl_sub.downloaders.soundcloud.abc import SoundcloudDownloaderOptions
from ytdl_sub.entries.soundcloud import SoundcloudTrack
from ytdl_sub.validators.url_validator import SoundcloudUsernameUrlValidator


class SoundcloudAlbumsAndSinglesDownloadOptions(SoundcloudDownloaderOptions):
    """
    Downloads a soundcloud user's entire discography. Groups together album tracks and considers
    any track not in an album as a single. Also includes any collaboration tracks.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          soundcloud:
            # required
            download_strategy: "albums_and_singles"
            url: "soundcloud.com/username"
            # optional
            skip_premiere_tracks: True

    """

    _required_keys = {"url"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._url = self._validate_key(
            key="url", validator=SoundcloudUsernameUrlValidator
        ).username_url

        self.collection_validator = CollectionDownloadOptions(
            name=self._name,
            value={
                "urls": [
                    {
                        "url": f"{self._url}/tracks",
                        "variables": {
                            "track_number": "1",
                            "track_number_padded": "01",
                            "track_count": "1",
                            "album": "{title}",
                            "album_sanitized": "{title_sanitized}",
                            "album_year": "{upload_year}",
                        },
                    },
                    {
                        "url": f"{self._url}/albums",
                        "variables": {
                            "track_number": "{playlist_index}",
                            "track_number_padded": "{playlist_index_padded}",
                            "track_count": "{playlist_count}",
                            "album": "{playlist}",
                            "album_sanitized": "{playlist_sanitized}",
                            "album_year": "{playlist_max_upload_year}",
                        },
                    },
                ]
            },
        )

    @property
    def url(self) -> str:
        """
        Required. The Soundcloud user's url, i.e. ``soundcloud.com/the_username``
        """
        return self._url


class SoundcloudAlbumsAndSinglesDownloader(
    SoundcloudDownloader[SoundcloudAlbumsAndSinglesDownloadOptions]
):
    downloader_options_type = SoundcloudAlbumsAndSinglesDownloadOptions
    supports_subtitles = False
    supports_chapters = False

    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        Default `ytdl_options`_ for ``albums_and_singles``

        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
             format: "bestaudio[ext=mp3]"  # download format the best possible mp3
        """
        return dict(
            super().ytdl_option_defaults(),
            **{
                "format": "bestaudio[ext=mp3]",
            },
        )

    def download(self) -> Generator[SoundcloudTrack, None, None]:
        """
        Soundcloud subscription to download albums and tracks as singles.
        """
        downloader = CollectionDownloader(
            download_options=self.download_options.collection_validator,
            enhanced_download_archive=self._enhanced_download_archive,
            ytdl_options_builder=self._ytdl_options_builder,
            overrides=self.overrides,
        )

        for entry in downloader.download():
            yield entry
