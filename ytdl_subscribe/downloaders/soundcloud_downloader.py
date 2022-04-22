from abc import ABC
from typing import Dict
from typing import List

from ytdl_subscribe.downloaders.downloader import Downloader
from ytdl_subscribe.downloaders.downloader import DownloaderValidator
from ytdl_subscribe.entries.soundcloud import SoundcloudAlbum
from ytdl_subscribe.entries.soundcloud import SoundcloudTrack
from ytdl_subscribe.validators.validators import BoolValidator
from ytdl_subscribe.validators.validators import StringValidator


class SoundcloudDownloaderValidator(DownloaderValidator, ABC):
    """
    Abstract source validator for all soundcloud sources.
    """

    _optional_keys = {"skip_premiere_tracks"}

    def __init__(self, name: str, value: dict):
        super().__init__(name=name, value=value)
        self.skip_premiere_tracks = self._validate_key(
            "skip_premiere_tracks", BoolValidator, default=True
        )


class SoundcloudDownloader(Downloader):
    """
    Class that handles downloading soundcloud entries via ytdl and converting them into
    SoundcloudTrack / SoundcloudAlbumTrack objects
    """

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

    def download_albums(self, artist_name: str) -> List[SoundcloudAlbum]:
        """
        Given an artist name, download all of their albums
        """
        artist_albums_url = f"{self.artist_url(artist_name)}/albums"

        info = self.extract_info(url=artist_albums_url)
        albums = [
            SoundcloudAlbum(working_direcotry=self.working_directory, **e) for e in info["entries"]
        ]

        return [album for album in albums if album.track_count > 0]

    def download_tracks(self, artist_name) -> List[SoundcloudTrack]:
        """
        Given an artist name, download all of their tracks
        """
        artist_tracks_url = f"{self.artist_url(artist_name)}/tracks"

        info = self.extract_info(url=artist_tracks_url)
        return [
            SoundcloudTrack(working_directory=self.working_directory, kwargs=e)
            for e in info["entries"]
        ]


class SoundcloudAlbumsAndSinglesSourceValidator(SoundcloudDownloaderValidator):
    _required_keys = {"username"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.username = self._validate_key(key="username", validator=StringValidator)
