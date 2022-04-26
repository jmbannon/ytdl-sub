import json
import os
from abc import ABC
from pathlib import Path
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar
from urllib.request import urlopen

from PIL.Image import Image
from PIL.Image import open as pil_open
from yt_dlp.utils import RejectedVideoReached

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.entries.youtube import YoutubeVideo
from ytdl_sub.validators.date_range_validator import DateRangeValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.validators import StringValidator

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

    def _download_using_metadata(
        self,
        url: str,
        ignore_prefix: str,
        ytdl_options_overrides: Optional[Dict] = None,
    ) -> List[YoutubeVideo]:
        """
        Do not get entries from the extract info, let it write to the info.json file and load
        that instead. This is because if the video is already downloaded in a playlist, it will
        not fetch the metadata (maybe there is a way??)
        """
        entries: List[YoutubeVideo] = []

        ytdl_overrides = {
            "writeinfojson": True,
        }
        if ytdl_options_overrides:
            ytdl_overrides = dict(ytdl_overrides, **ytdl_options_overrides)

        try:
            _ = self.extract_info(ytdl_options_overrides=ytdl_overrides, url=url)
        except RejectedVideoReached:
            pass

        # Load the entries from info.json, ignore the playlist entry
        for file_name in os.listdir(self.working_directory):
            if file_name.startswith(ignore_prefix) or not file_name.endswith(".info.json"):
                continue

            with open(Path(self.working_directory) / file_name, "r", encoding="utf-8") as file:
                entries.append(
                    YoutubeVideo(
                        entry_dict=json.load(file), working_directory=self.working_directory
                    )
                )

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

    @classmethod
    def video_url(cls, video_id: str) -> str:
        """Returns full video url"""
        return f"https://youtube.com/watch?v={video_id}"

    def download(self) -> List[YoutubeVideo]:
        """Download a single Youtube video"""
        video_id = self.download_options.video_id.value
        video_url = self.video_url(video_id=video_id)

        entry = self.extract_info(url=video_url)
        return [YoutubeVideo(entry_dict=entry, working_directory=self.working_directory)]


###############################################################################
# Youtube playlist downloader + options


class YoutubePlaylistDownloaderOptions(YoutubeDownloaderOptions):
    _required_keys = {"playlist_id"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.playlist_id = self._validate_key("playlist_id", StringValidator)


class YoutubePlaylistDownloader(YoutubeDownloader[YoutubePlaylistDownloaderOptions]):
    downloader_options_type = YoutubePlaylistDownloaderOptions

    @classmethod
    def playlist_url(cls, playlist_id: str) -> str:
        """Returns full playlist url"""
        return f"https://youtube.com/playlist?list={playlist_id}"

    def download(self) -> List[YoutubeVideo]:
        """
        Downloads all videos in a Youtube playlist
        """
        playlist_id = self.download_options.playlist_id.value
        playlist_url = self.playlist_url(playlist_id=playlist_id)

        return self._download_using_metadata(url=playlist_url, ignore_prefix=playlist_id)


###############################################################################
# Youtube channel downloader + options


class YoutubeChannelDownloaderOptions(YoutubeDownloaderOptions, DateRangeValidator):
    _required_keys = {"channel_id"}
    _optional_keys = {"before", "after", "channel_avatar_path", "channel_banner_path"}

    def __init__(self, name, value):
        YoutubeDownloaderOptions.__init__(self, name, value)
        DateRangeValidator.__init__(self, name, value)
        self.channel_id = self._validate_key("channel_id", StringValidator)
        self.channel_avatar_path = self._validate_key_if_present(
            "channel_avatar_path", OverridesStringFormatterValidator
        )
        self.channel_banner_path = self._validate_key_if_present(
            "channel_banner_path", OverridesStringFormatterValidator
        )


class YoutubeChannelDownloader(YoutubeDownloader[YoutubeChannelDownloaderOptions]):
    downloader_options_type = YoutubeChannelDownloaderOptions

    @classmethod
    def channel_url(cls, channel_id: str) -> str:
        """Returns full channel url"""
        return f"https://youtube.com/channel/{channel_id}"

    @property
    def channel_id(self) -> str:
        """
        Returns
        -------
        Channel ID
        """
        return self.download_options.channel_id.value

    def download(self) -> List[YoutubeVideo]:
        """
        Downloads all videos from a channel
        """
        channel_url = self.channel_url(channel_id=self.channel_id)

        # If a date range is specified when download a YT channel, add it into the ytdl options
        ytdl_options_overrides = {}
        source_date_range = self.download_options.get_date_range()
        if source_date_range:
            ytdl_options_overrides["daterange"] = source_date_range

        return self._download_using_metadata(
            url=channel_url,
            ignore_prefix=self.channel_id,
            ytdl_options_overrides=ytdl_options_overrides,
        )

    def __download_thumbnail(
        self,
        channel_dict: dict,
        thumbnail_id: str,
        output_thumbnail_path: str,
    ):
        thumbnail_url = None
        for thumbnail in channel_dict.get("thumbnails", []):
            if thumbnail["id"] == thumbnail_id:
                thumbnail_url = thumbnail["url"]
                break

        if not thumbnail_url:
            # TODO: add logger with warn here
            return

        with urlopen(thumbnail_url) as file:
            image: Image = pil_open(file).convert("RGB")

        image.save(fp=output_thumbnail_path, format="jpeg")

    def post_download(self, overrides: Overrides, output_directory: str):
        """
        Downloads and moves channel avatar and banner images to the output directory.

        Parameters
        ----------
        overrides
            Overrides that can contain variables in the avatar or banner file path
        output_directory
            Output directory path
        """
        channel_json_file_path = Path(self.working_directory) / f"{self.channel_id}.info.json"
        with open(channel_json_file_path) as channel_json:
            channel_entry = json.load(channel_json)

        if self.download_options.channel_avatar_path:
            thumbnail_name = overrides.apply_formatter(self.download_options.channel_avatar_path)
            self.__download_thumbnail(
                channel_dict=channel_entry,
                thumbnail_id="avatar_uncropped",
                output_thumbnail_path=str(Path(output_directory) / thumbnail_name),
            )

        if self.download_options.channel_banner_path:
            thumbnail_name = overrides.apply_formatter(self.download_options.channel_banner_path)
            self.__download_thumbnail(
                channel_dict=channel_entry,
                thumbnail_id="banner_uncropped",
                output_thumbnail_path=str(Path(output_directory) / thumbnail_name),
            )
