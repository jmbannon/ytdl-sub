from abc import ABC
from typing import Generic
from typing import TypeVar

from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.entries.youtube import YoutubeVideo


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
