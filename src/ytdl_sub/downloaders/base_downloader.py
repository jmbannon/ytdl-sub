import abc
from abc import ABC
from typing import Generic
from typing import Iterable
from typing import List
from typing import Type
from typing import TypeVar

from ytdl_sub.config.preset_options import AddsVariablesMixin
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadArchiver
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class BaseDownloaderValidator(StrictDictValidator, AddsVariablesMixin, ABC):
    pass


BaseDownloaderOptionsT = TypeVar("BaseDownloaderOptionsT", bound=BaseDownloaderValidator)


class BaseDownloaderPluginOptions(PluginOptions):
    _optional_keys = {"no-op"}


class BaseDownloaderPlugin(Plugin[BaseDownloaderPluginOptions], ABC):
    def __init__(
        self,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        super().__init__(
            # Downloader plugins do not have exposed YAML options, so keep it blank.
            # Use init instead.
            plugin_options=BaseDownloaderPluginOptions(name=self.__class__.__name__, value={}),
            overrides=overrides,
            enhanced_download_archive=enhanced_download_archive,
        )


class BaseDownloader(DownloadArchiver, Generic[BaseDownloaderOptionsT], ABC):
    downloader_options_type: Type[BaseDownloaderOptionsT]

    def __init__(
        self,
        download_options: BaseDownloaderOptionsT,
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

    # pylint: disable=no-self-use
    def added_plugins(self) -> List[BaseDownloaderPlugin]:
        """Add these plugins from the Downloader to the subscription"""
        return []

    # pylint: enable=no-self-use
