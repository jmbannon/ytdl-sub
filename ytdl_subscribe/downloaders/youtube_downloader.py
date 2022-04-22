import json
import os
from abc import ABC
from pathlib import Path
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from yt_dlp.utils import RejectedVideoReached

from ytdl_subscribe.downloaders.downloader import Downloader
from ytdl_subscribe.downloaders.downloader import DownloaderValidator
from ytdl_subscribe.entries.youtube import YoutubeVideo
from ytdl_subscribe.validators.date_range_validator import DownloadDateRangeSource
from ytdl_subscribe.validators.validators import StringValidator

###############################################################################
# Abstract Youtube downloader + options


class YoutubeDownloaderOptions(DownloaderValidator, ABC):
    """
    Abstract source validator for all soundcloud sources.
    """


YoutubeDownloaderOptionsT = TypeVar("YoutubeDownloaderOptionsT", bound=YoutubeDownloaderOptions)


class YoutubeDownloader(
    Downloader[YoutubeDownloaderOptionsT, YoutubeVideo], Generic[YoutubeDownloaderOptionsT], ABC
):
    """
    Class that handles downloading youtube entries via ytdl and converting them into
    YoutubeVideo objects
    """

    downloader_entry_type = YoutubeVideo

    @classmethod
    def playlist_url(cls, playlist_id: str) -> str:
        """Returns full playlist url"""
        return f"https://youtube.com/playlist?list={playlist_id}"

    @classmethod
    def video_url(cls, video_id: str) -> str:
        """Returns full video url"""
        return f"https://youtube.com/watch?v={video_id}"

    @classmethod
    def channel_url(cls, channel_id: str) -> str:
        """Returns full channel url"""
        return f"https://youtube.com/channel/{channel_id}"

    def _download_with_metadata(
        self, url: str, ytdl_options_overrides: Optional[Dict] = None
    ) -> None:
        """
        Do not get entries from the extract info, let it write to the info.json file and load
        that instead. This is because if the video is already downloaded in a playlist, it will
        not fetch the metadata (maybe there is a way??)
        """
        ytdl_overrides = {
            "writeinfojson": True,
        }
        if ytdl_options_overrides:
            ytdl_overrides = dict(ytdl_overrides, **ytdl_options_overrides)

        try:
            _ = self.extract_info(ytdl_options_overrides=ytdl_overrides, url=url)
        except RejectedVideoReached:
            pass

    def download_video(self, video_id: str) -> YoutubeVideo:
        """Download a single Youtube video"""
        entry = self.extract_info(url=self.video_url(video_id))
        return YoutubeVideo(**entry)

    def download_playlist(self, playlist_id: str) -> List[YoutubeVideo]:
        """
        Downloads all videos in a Youtube playlist
        """
        playlist_url = self.playlist_url(playlist_id=playlist_id)

        self._download_with_metadata(url=playlist_url)

        # Load the entries from info.json, ignore the playlist entry
        entries: List[YoutubeVideo] = []

        # Load the entries from info.json, ignore the playlist entry
        for file_name in os.listdir(self.working_directory):
            if file_name.endswith(".info.json") and not file_name.startswith(playlist_id):
                with open(Path(self.working_directory) / file_name, "r", encoding="utf-8") as file:
                    entries.append(YoutubeVideo(**json.load(file)))

        return entries

    def download_channel(
        self, channel_id: str, ytdl_options_overrides: Optional[Dict] = None
    ) -> List[YoutubeVideo]:
        """
        Downloads all videos from a channel
        """
        self._download_with_metadata(
            url=self.channel_url(channel_id), ytdl_options_overrides=ytdl_options_overrides
        )

        # Load the entries from info.json
        entries: List[YoutubeVideo] = []

        # Load the entries from info.json
        # TODO dupe code between this and playlist
        for file_name in os.listdir(self.working_directory):
            if file_name.endswith(".info.json") and not file_name.startswith(channel_id):
                with open(Path(self.working_directory) / file_name, "r", encoding="utf-8") as file:
                    entries.append(YoutubeVideo(**json.load(file)))

        return entries


###############################################################################
# Youtube single video downloader + options


class YoutubeVideoDownloaderOptions(YoutubeDownloaderOptions):
    _required_keys = {"video_id"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.video_id = self._validate_key("video_id", StringValidator)


class YoutubeVideoDownloader(YoutubeDownloader[YoutubeVideoDownloaderOptions]):
    downloader_options_type = YoutubeVideoDownloaderOptions

    def download(self) -> List[YoutubeVideo]:
        video = self.download_video(video_id=self.download_options.video_id.value)
        return [video]


###############################################################################
# Youtube playlist downloader + options


class YoutubePlaylistDownloaderOptions(YoutubeDownloaderOptions):
    _required_keys = {"playlist_id"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.playlist_id = self._validate_key("playlist_id", StringValidator)


class YoutubePlaylistDownloader(YoutubeDownloader[YoutubePlaylistDownloaderOptions]):
    downloader_options_type = YoutubePlaylistDownloaderOptions

    def download(self) -> List[YoutubeVideo]:
        return self.download_playlist(playlist_id=self.download_options.playlist_id.value)


###############################################################################
# Youtube channel downloader + options


class YoutubeChannelDownloaderOptions(YoutubeDownloaderOptions, DownloadDateRangeSource):
    _required_keys = {"channel_id"}
    _optional_keys = {"before", "after"}

    def __init__(self, name, value):
        YoutubeDownloaderOptions.__init__(self, name, value)
        DownloadDateRangeSource.__init__(self, name, value)
        self.channel_id = self._validate_key("channel_id", StringValidator)


class YoutubeChannelDownloader(YoutubeDownloader[YoutubeChannelDownloaderOptions]):
    downloader_options_type = YoutubeChannelDownloaderOptions

    def download(self) -> List[YoutubeVideo]:
        ytdl_options_overrides = {}
        source_date_range = self.download_options.get_date_range()
        if source_date_range:
            ytdl_options_overrides["daterange"] = source_date_range

        return self.download_channel(
            channel_id=self.download_options.channel_id.value,
            ytdl_options_overrides=ytdl_options_overrides,
        )
