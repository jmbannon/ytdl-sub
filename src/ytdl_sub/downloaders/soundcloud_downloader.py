from abc import ABC
from typing import Dict
from typing import Generic
from typing import List
from typing import TypeVar

from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.entries.soundcloud import SoundcloudAlbum
from ytdl_sub.entries.soundcloud import SoundcloudTrack
from ytdl_sub.validators.url_validator import SoundcloudUsernameUrlValidator
from ytdl_sub.validators.validators import BoolValidator

###############################################################################
# Abstract Soundcloud downloader + options


class SoundcloudDownloaderOptions(DownloaderValidator, ABC):
    """
    Abstract source validator for all soundcloud sources.
    """

    _optional_keys = {"skip_premiere_tracks"}

    def __init__(self, name: str, value: dict):
        super().__init__(name=name, value=value)
        self._skip_premiere_tracks = self._validate_key(
            "skip_premiere_tracks", BoolValidator, default=True
        )

    @property
    def skip_premiere_tracks(self) -> bool:
        """
        Optional. True to skip tracks that require purchasing. False otherwise. Defaults to True.
        """
        return self._skip_premiere_tracks.value


SoundcloudDownloaderOptionsT = TypeVar(
    "SoundcloudDownloaderOptionsT", bound=SoundcloudDownloaderOptions
)


class SoundcloudDownloader(
    Downloader[SoundcloudDownloaderOptionsT, SoundcloudTrack],
    Generic[SoundcloudDownloaderOptionsT],
    ABC,
):
    """
    Class that handles downloading soundcloud entries via ytdl and converting them into
    SoundcloudTrack / SoundcloudAlbumTrack objects
    """

    downloader_entry_type = SoundcloudTrack

    @classmethod
    def artist_albums_url(cls, artist_url: str) -> str:
        """
        Returns
        -------
        Full artist album url
        """
        return f"{artist_url}/albums"

    @classmethod
    def artist_tracks_url(cls, artist_url: str) -> str:
        """
        Returns
        -------
        Full artist tracks url
        """
        return f"{artist_url}/tracks"


###############################################################################
# Soundcloud albums and singles downloader + options


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

    def _get_albums(self, entry_dicts: List[Dict]) -> List[SoundcloudAlbum]:
        """
        Parameters
        ----------
        entry_dicts
            Entry dicts from extracting info jsons

        Returns
        -------
        Dict containing album_id: album class
        """
        albums: Dict[str, SoundcloudAlbum] = {}

        # First, get the albums themselves
        for entry_dict in entry_dicts:
            if entry_dict.get("extractor") == "soundcloud:set":
                albums[entry_dict["id"]] = SoundcloudAlbum(
                    entry_dict=entry_dict, working_directory=self.working_directory
                )

        # Then, get all tracks that belong to the album
        for entry_dict in entry_dicts:
            album_id = entry_dict.get("playlist_id")
            if entry_dict.get("extractor") == "soundcloud" and album_id in albums:
                albums[album_id].tracks.append(
                    SoundcloudTrack(entry_dict=entry_dict, working_directory=self.working_directory)
                )

        return list(albums.values())

    def _get_singles(
        self, entry_dicts: List[Dict], albums: List[SoundcloudAlbum]
    ) -> List[SoundcloudTrack]:
        tracks: List[SoundcloudTrack] = []

        # Get all tracks that are not part of an album
        for entry_dict in entry_dicts:
            if entry_dict.get("extractor") == "soundcloud" and not any(
                entry_dict in album for album in albums
            ):
                tracks.append(
                    SoundcloudTrack(entry_dict=entry_dict, working_directory=self.working_directory)
                )

        return tracks

    def download(self) -> List[SoundcloudTrack]:
        """
        Soundcloud subscription to download albums and tracks as singles.
        """
        artist_albums_url = self.artist_albums_url(artist_url=self.download_options.url)
        artist_tracks_url = self.artist_tracks_url(artist_url=self.download_options.url)

        album_entry_dicts = self.extract_info_via_info_json(url=artist_albums_url)
        tracks_entry_dicts = self.extract_info_via_info_json(url=artist_tracks_url)

        # Get all of the artist's albums
        albums = self._get_albums(entry_dicts=album_entry_dicts)

        # Then, get all singles
        tracks = self._get_singles(entry_dicts=tracks_entry_dicts, albums=albums)

        # Append all album tracks as SoundcloudAlbumTrack classes to the singles
        for album in albums:
            tracks += album.album_tracks()

        # Filter any premiere tracks if specified
        if self.download_options.skip_premiere_tracks:
            tracks = [track for track in tracks if not track.is_premiere()]

        return tracks
