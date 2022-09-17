from typing import Dict
from typing import Generator

from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.downloaders.generic.collection_validator import CollectionValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.validators.url_validator import SoundcloudUsernameUrlValidator
from ytdl_sub.validators.validators import BoolValidator


class SoundcloudAlbumsAndSinglesDownloadOptions(DownloaderValidator):
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
    _optional_keys = {"skip_premiere_tracks"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._url = self._validate_key(
            key="url", validator=SoundcloudUsernameUrlValidator
        ).username_url
        self._skip_premiere_tracks = self._validate_key(
            "skip_premiere_tracks", BoolValidator, default=True
        )

    @property
    def collection_validator(self) -> CollectionValidator:
        """Downloads the album tracks first, then the tracks"""
        return CollectionValidator(
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
                            "album": "{playlist_title}",
                            "album_sanitized": "{playlist_title_sanitized}",
                            "album_year": "{playlist_max_upload_year}",
                        },
                    },
                ]
            },
        )

    @property
    def skip_premiere_tracks(self) -> bool:
        """
        Optional. True to skip tracks that require purchasing. False otherwise. Defaults to True.
        """
        return self._skip_premiere_tracks.value

    @property
    def url(self) -> str:
        """
        Required. The Soundcloud user's url, i.e. ``soundcloud.com/the_username``
        """
        return self._url


class SoundcloudAlbumsAndSinglesDownloader(
    Downloader[SoundcloudAlbumsAndSinglesDownloadOptions, Entry]
):
    downloader_options_type = SoundcloudAlbumsAndSinglesDownloadOptions
    downloader_entry_type = Entry

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

    def _should_skip(self, entry: Entry) -> bool:
        if not self.download_options.skip_premiere_tracks:
            return False

        for url in [entry.kwargs_get("url", ""), entry.webpage_url]:
            if "/preview/" in url:
                return True

        return False

    def download(self) -> Generator[Entry, None, None]:
        """
        Soundcloud subscription to download albums and tracks as singles.
        """
        for entry in super().download():
            if self._should_skip(entry):
                continue

            yield entry
