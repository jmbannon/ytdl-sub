import json
import os
from pathlib import Path
from typing import List

from ytdl_subscribe.downloaders.downloader import Downloader
from ytdl_subscribe.entries.youtube import YoutubeVideo


class YoutubeDownloader(Downloader):
    """
    Class that handles downloading youtube entries via ytdl and converting them into
    YoutubeVideo objects
    """

    @classmethod
    def playlist_url(cls, playlist_id: str) -> str:
        """Returns full playlist url"""
        return f"https://youtube.com/playlist?list={playlist_id}"

    def _download_with_metadata(self, url: str) -> None:
        """
        Do not get entries from the extract info, let it write to the info.json file and load
        that instead. This is because if the video is already downloaded in a playlist, it will
        not fetch the metadata (maybe there is a way??)
        """
        ytdl_metadata_override = {
            "download_archive": str(
                Path(self.working_directory) / "ytdl-download-archive.txt"
            ),
            "writeinfojson": True,
        }
        _ = self.extract_info(ytdl_options_overrides=ytdl_metadata_override, url=url)

    def download_playlist(self, playlist_id: str) -> List[YoutubeVideo]:
        """
        Downloads all videos in a playlist
        """
        playlist_url = self.playlist_url(playlist_id=playlist_id)

        self._download_with_metadata(url=playlist_url)

        # Load the entries from info.json, ignore the playlist entry
        entries: List[YoutubeVideo] = []

        # Load the entries from info.json, ignore the playlist entry
        for file_name in os.listdir(self.working_directory):
            if file_name.endswith(".info.json") and not file_name.startswith(
                playlist_id
            ):
                with open(
                    Path(self.working_directory) / file_name, "r", encoding="utf-8"
                ) as file:
                    entries.append(YoutubeVideo(**json.load(file)))

        return entries
