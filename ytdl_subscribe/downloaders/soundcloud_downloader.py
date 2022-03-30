from typing import Dict
from typing import List

from ytdl_subscribe.downloaders.downloader import Downloader
from ytdl_subscribe.entries.soundcloud import SoundcloudAlbum
from ytdl_subscribe.entries.soundcloud import SoundcloudTrack


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
        return [SoundcloudAlbum(**e) for e in info["entries"]]

    def download_tracks(self, artist_name) -> List[SoundcloudTrack]:
        """
        Given an artist name, download all of their tracks
        """
        artist_tracks_url = f"{self.artist_url(artist_name)}/tracks"

        info = self.extract_info(url=artist_tracks_url)
        return [SoundcloudTrack(**e) for e in info["entries"]]
