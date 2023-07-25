import abc
from abc import ABC
from typing import Generic
from typing import Iterable
from typing import List
from typing import Type

from ytdl_sub.config.plugin import Plugin
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.config.preset_options import TOptionsValidator
from ytdl_sub.downloaders.downloader_validator import TDownloaderValidator
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadArchiver
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class BaseDownloaderPlugin(Plugin[TDownloaderValidator], ABC):
    """
    Plugins that get added automatically by using a downloader. Downloader options
    are the plugin options.
    """

    def __init__(
        self,
        downloader_options: TDownloaderValidator,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        super().__init__(
            # Downloader plugins use download options as their plugin options
            options=downloader_options,
            overrides=overrides,
            enhanced_download_archive=enhanced_download_archive,
        )


class BaseDownloader(DownloadArchiver, Generic[TOptionsValidator], ABC):
    downloader_options_type: Type[TOptionsValidator]

    def __init__(
        self,
        download_options: TOptionsValidator,
        enhanced_download_archive: EnhancedDownloadArchive,
        download_ytdl_options: YTDLOptionsBuilder,
        metadata_ytdl_options: YTDLOptionsBuilder,
        overrides: Overrides,
    ):
        super().__init__(enhanced_download_archive=enhanced_download_archive)
        self.download_options = download_options
        self.overrides = overrides
        self._download_ytdl_options_builder = download_ytdl_options
        self._metadata_ytdl_options_builder = metadata_ytdl_options

    @abc.abstractmethod
    def download_metadata(self) -> Iterable[Entry]:
        """Gathers metadata of all entries to download"""

    @abc.abstractmethod
    def download(self, entry: Entry) -> Entry:
        """The function to perform the download of all media entries"""

    # pylint: disable=unused-argument
    @classmethod
    def added_plugins(
        cls,
        downloader_options: TOptionsValidator,
        enhanced_download_archive: EnhancedDownloadArchive,
        overrides: Overrides,
    ) -> List[BaseDownloaderPlugin]:
        """Add these plugins from the Downloader to the subscription"""
        return []

    # pylint: enable=unused-argument
