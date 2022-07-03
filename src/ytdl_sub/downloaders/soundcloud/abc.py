from abc import ABC
from typing import Generic
from typing import TypeVar

from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.entries.soundcloud import SoundcloudTrack
from ytdl_sub.validators.validators import BoolValidator


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
