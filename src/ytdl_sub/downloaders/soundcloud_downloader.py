from abc import ABC
from typing import Dict
from typing import Generic
from typing import List
from typing import TypeVar

from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.entries.soundcloud import SoundcloudAlbum
from ytdl_sub.entries.soundcloud import SoundcloudTrack
from ytdl_sub.validators.validators import BoolValidator
from ytdl_sub.validators.validators import StringValidator

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
    def ytdl_option_defaults(cls) -> Dict:
        """Returns default format to be best mp3"""
        return {
            "format": "bestaudio[ext=mp3]",
        }

    @classmethod
    def artist_url(cls, artist_name: str) -> str:
        """Returns full artist url"""
        return f"https://soundcloud.com/{artist_name}"


###############################################################################
# Soundcloud albums and singles downloader + options


class SoundcloudAlbumsAndSinglesDownloadOptions(SoundcloudDownloaderOptions):
    _required_keys = {"username"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._username = self._validate_key(key="username", validator=StringValidator)

    @property
    def username(self) -> str:
        """
        Required. The Soundcloud username found in the url of their page.
        """
        return self._username.value


class SoundcloudAlbumsAndSinglesDownloader(
    SoundcloudDownloader[SoundcloudAlbumsAndSinglesDownloadOptions]
):
    downloader_options_type = SoundcloudAlbumsAndSinglesDownloadOptions

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

    def _get_singles(self, entry_dicts: List[Dict]) -> List[SoundcloudTrack]:
        artist_id = None
        tracks: List[SoundcloudTrack] = []

        # First, get the artist entry. All single tracks that do not belong to an album will belong
        # to the 'artist' playlist
        for entry_dict in entry_dicts:
            if entry_dict.get("extractor") == "soundcloud:user":
                artist_id = entry_dict["id"]

        # Then, get all singles that belong to the 'artist' playlist
        for entry_dict in entry_dicts:
            if (
                entry_dict.get("extractor") == "soundcloud"
                and entry_dict.get("playlist_id") == artist_id
            ):
                tracks.append(
                    SoundcloudTrack(entry_dict=entry_dict, working_directory=self.working_directory)
                )

        return tracks

    def download(self) -> List[SoundcloudTrack]:
        """
        Soundcloud subscription to download albums and tracks as singles.
        """
        artist_url = self.artist_url(artist_name=self.download_options.username)
        entry_dicts = self.extract_info_via_info_json(url=artist_url)

        # Get all of the artist's albums
        albums = self._get_albums(entry_dicts=entry_dicts)

        # Then, get all singles
        tracks = self._get_singles(entry_dicts=entry_dicts)

        # Append all album tracks as SoundcloudAlbumTrack classes to the singles
        for album in albums:
            tracks += album.album_tracks()

        # Filter any premiere tracks if specified
        if self.download_options.skip_premiere_tracks:
            tracks = [track for track in tracks if not track.is_premiere()]

        return tracks
