from typing import Dict
from typing import List

from ytdl_subscribe.downloaders.downloader import Downloader
from ytdl_subscribe.entries.soundcloud import SoundcloudAlbum
from ytdl_subscribe.entries.soundcloud import SoundcloudTrack


class SoundcloudDownloader(Downloader):
    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        return {
            "format": "bestaudio[ext=mp3]",
        }

    @classmethod
    def artist_url(cls, artist_name: str) -> str:
        return f"https://soundcloud.com/{artist_name}"

    def download_albums(self, artist_name) -> List[SoundcloudAlbum]:
        artist_albums_url = f"{self.artist_url(artist_name)}/albums"

        info = self.extract_info(url=artist_albums_url)
        return [SoundcloudAlbum(**e) for e in info["entries"]]

    def download_tracks(self, artist_name) -> List[SoundcloudTrack]:
        artist_tracks_url = f"{self.artist_url(artist_name)}/tracks"

        info = self.extract_info(url=artist_tracks_url)
        return [SoundcloudTrack(**e) for e in info["entries"]]
