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
        self.skip_premiere_tracks = self._validate_key(
            "skip_premiere_tracks", BoolValidator, default=True
        )


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

    def download_albums(self, artist_name: str) -> List[SoundcloudAlbum]:
        """
        Given an artist name, download all of their albums
        """
        artist_albums_url = f"{self.artist_url(artist_name)}/albums"

        info = self.extract_info(url=artist_albums_url)
        albums = [
            SoundcloudAlbum(entry_dict=e, working_directory=self.working_directory)
            for e in info["entries"]
        ]

        return [album for album in albums if album.track_count > 0]

    def download_tracks(self, artist_name) -> List[SoundcloudTrack]:
        """
        Given an artist name, download all of their tracks
        """
        artist_tracks_url = f"{self.artist_url(artist_name)}/tracks"

        info = self.extract_info(url=artist_tracks_url)
        return [
            SoundcloudTrack(entry_dict=e, working_directory=self.working_directory)
            for e in info["entries"]
        ]


###############################################################################
# Soundcloud albums and singles downloader + options


class SoundcloudAlbumsAndSinglesDownloadOptions(SoundcloudDownloaderOptions):
    _required_keys = {"username"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.username = self._validate_key(key="username", validator=StringValidator)


class SoundcloudAlbumsAndSinglesDownloader(
    SoundcloudDownloader[SoundcloudAlbumsAndSinglesDownloadOptions]
):
    downloader_options_type = SoundcloudAlbumsAndSinglesDownloadOptions

    def download(self) -> List[SoundcloudTrack]:
        """
        Soundcloud subscription to download albums and tracks as singles.
        """
        tracks: List[SoundcloudTrack] = []

        # Get the album info first. This tells us which track ids belong
        # to an album. Unfortunately we cannot use download_archive or info.json for this
        albums: List[SoundcloudAlbum] = self.download_albums(
            artist_name=self.download_options.username.value
        )

        for album in albums:
            tracks += album.album_tracks(
                skip_premiere_tracks=self.download_options.skip_premiere_tracks.value
            )

        # only add tracks that are not part of an album
        single_tracks = self.download_tracks(artist_name=self.download_options.username.value)
        tracks += [
            track for track in single_tracks if not any(album.contains(track) for album in albums)
        ]

        return tracks
