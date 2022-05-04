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

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderOptionsT
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.entries.youtube import YoutubeChannel
from ytdl_sub.entries.youtube import YoutubePlaylistVideo
from ytdl_sub.entries.youtube import YoutubeVideo
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.date_range_validator import DateRangeValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.validators import StringValidator

logger = Logger.get()

###############################################################################
# Abstract Youtube downloader + options


class YoutubeDownloaderOptions(DownloaderValidator, ABC):
    """
    Abstract source validator for all soundcloud sources.
    """


YoutubeDownloaderOptionsT = TypeVar("YoutubeDownloaderOptionsT", bound=YoutubeDownloaderOptions)
YoutubeVideoT = TypeVar("YoutubeVideoT", bound=YoutubeVideo)


class YoutubeDownloader(
    Downloader[YoutubeDownloaderOptionsT, YoutubeVideoT],
    Generic[YoutubeDownloaderOptionsT, YoutubeVideoT],
    ABC,
):
    """
    Class that handles downloading youtube entries via ytdl and converting them into
    YoutubeVideo like objects. Reserved for any future logic that is shared amongst all YT
    downloaders.
    """


###############################################################################
# Youtube single video downloader + options


class YoutubeVideoDownloaderOptions(YoutubeDownloaderOptions):
    _required_keys = {"video_id"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.video_id = self._validate_key("video_id", StringValidator)


class YoutubeVideoDownloader(YoutubeDownloader[YoutubeVideoDownloaderOptions, YoutubeVideo]):
    downloader_options_type = YoutubeVideoDownloaderOptions
    downloader_entry_type = YoutubeVideo

    @classmethod
    def video_url(cls, video_id: str) -> str:
        """Returns full video url"""
        return f"https://youtube.com/watch?v={video_id}"

    def download(self) -> List[YoutubeVideo]:
        """Download a single Youtube video"""
        video_id = self.download_options.video_id.value
        video_url = self.video_url(video_id=video_id)

        entry_dict = self.extract_info(url=video_url)
        return [YoutubeVideo(entry_dict=entry_dict, working_directory=self.working_directory)]


###############################################################################
# Youtube playlist downloader + options


class YoutubePlaylistDownloaderOptions(YoutubeDownloaderOptions):
    _required_keys = {"playlist_id"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.playlist_id = self._validate_key("playlist_id", StringValidator)


class YoutubePlaylistDownloader(
    YoutubeDownloader[YoutubePlaylistDownloaderOptions, YoutubePlaylistVideo]
):
    downloader_options_type = YoutubePlaylistDownloaderOptions
    downloader_entry_type = YoutubePlaylistVideo

    @classmethod
    def playlist_url(cls, playlist_id: str) -> str:
        """Returns full playlist url"""
        return f"https://youtube.com/playlist?list={playlist_id}"

    def download(self) -> List[YoutubePlaylistVideo]:
        """
        Downloads all videos in a Youtube playlist
        """
        playlist_id = self.download_options.playlist_id.value
        playlist_url = self.playlist_url(playlist_id=playlist_id)
        playlist_videos: List[YoutubePlaylistVideo] = []

        entry_dicts = self.extract_info_via_info_json(url=playlist_url)
        for entry_dict in entry_dicts:
            if entry_dict.get("extractor") == "youtube":
                playlist_videos.append(
                    YoutubePlaylistVideo(
                        entry_dict=entry_dict, working_directory=self.working_directory
                    )
                )

        return playlist_videos


###############################################################################
# Youtube channel downloader + options


class YoutubeChannelDownloaderOptions(YoutubeDownloaderOptions, DateRangeValidator):
    _required_keys = {"channel_id"}
    _optional_keys = {"before", "after", "channel_avatar_path", "channel_banner_path"}

    def __init__(self, name, value):
        YoutubeDownloaderOptions.__init__(self, name, value)
        DateRangeValidator.__init__(self, name, value)
        self._channel_id = self._validate_key("channel_id", StringValidator)
        self._channel_avatar_path = self._validate_key_if_present(
            "channel_avatar_path", OverridesStringFormatterValidator
        )
        self._channel_banner_path = self._validate_key_if_present(
            "channel_banner_path", OverridesStringFormatterValidator
        )

    @property
    def channel_id(self) -> str:
        """
        The channel's ID. Not to be confused with the username. It should look something like
        `UCsvn_Po0SmunchJYOWpOxMg`. You can get this by opening a video and clicking on the
        channel's avatar image to take you to their channel, then check the url.
        """
        return self.channel_id

    @property
    def channel_avatar_path(self) -> Optional[OverridesStringFormatterValidator]:
        """
        Optional. Path to store the channel's avatar thumbnail image to.
        """
        return self._channel_avatar_path

    @property
    def channel_banner_path(self) -> Optional[OverridesStringFormatterValidator]:
        """
        Optional. Path to store the channel's banner image to.
        """
        return self._channel_banner_path


class YoutubeChannelDownloader(YoutubeDownloader[YoutubeChannelDownloaderOptions, YoutubeVideo]):
    downloader_options_type = YoutubeChannelDownloaderOptions
    downloader_entry_type = YoutubeVideo

    def __init__(
        self,
        working_directory: str,
        download_options: DownloaderOptionsT,
        ytdl_options: Optional[Dict] = None,
        download_archive_file_name: Optional[str] = None,
    ):
        super().__init__(
            working_directory=working_directory,
            download_options=download_options,
            ytdl_options=ytdl_options,
            download_archive_file_name=download_archive_file_name,
        )
        self.channel: Optional[YoutubeChannel] = None

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
        channel_videos: List[YoutubeVideo] = []
        ytdl_options_overrides = {}

        # If a date range is specified when download a YT channel, add it into the ytdl options
        source_date_range = self.download_options.get_date_range()
        if source_date_range:
            ytdl_options_overrides["daterange"] = source_date_range

        entry_dicts = self.extract_info_via_info_json(
            ytdl_options_overrides=ytdl_options_overrides, url=channel_url
        )

        for entry_dict in entry_dicts:
            if entry_dict.get("extractor") == "youtube":
                channel_videos.append(
                    YoutubeVideo(entry_dict=entry_dict, working_directory=self.working_directory)
                )
            if entry_dict.get("extractor") == "youtube:tab":
                self.channel = YoutubeChannel(
                    entry_dict=entry_dict, working_directory=self.working_directory
                )

        return channel_videos

    def _download_thumbnail(
        self,
        thumbnail_url: str,
        output_thumbnail_path: str,
    ):
        """
        Downloads a thumbnail and stores it in the output directory

        Parameters
        ----------
        thumbnail_url:
            Url of the thumbnail
        output_thumbnail_path:
            Path to store the thumbnail after downloading
        """
        if not thumbnail_url:
            logger.warning("Could not find a thumbnail for %s", self.channel.uid)
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
        avatar_thumbnail_name = overrides.apply_formatter(self.download_options.channel_avatar_path)
        self._download_thumbnail(
            thumbnail_url=self.channel.avatar_thumbnail_url(),
            output_thumbnail_path=str(Path(output_directory) / avatar_thumbnail_name),
        )

        banner_thumbnail_name = overrides.apply_formatter(self.download_options.channel_banner_path)
        self._download_thumbnail(
            thumbnail_url=self.channel.banner_thumbnail_url(),
            output_thumbnail_path=str(Path(output_directory) / banner_thumbnail_name),
        )
