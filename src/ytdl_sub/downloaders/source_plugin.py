import abc
from abc import ABC
from typing import Dict
from typing import Generic
from typing import Iterable
from typing import List
from typing import Optional
from typing import Type
from typing import final

from ytdl_sub.config.plugin import BasePlugin
from ytdl_sub.config.plugin import Plugin
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.config.preset_options import TOptionsValidator
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class SourcePluginExtension(Plugin[TOptionsValidator], ABC):
    """
    Plugins that get added automatically by using a downloader. Downloader options
    are the plugin options.
    """

    @final
    def ytdl_options(self) -> Optional[Dict]:
        """
        SourcePluginExtensions are intended to run after downloading. ytdl_options at that point
        are not needed.
        """
        return None


class SourcePlugin(BasePlugin[TOptionsValidator], Generic[TOptionsValidator], ABC):
    plugin_extensions: List[Type[SourcePluginExtension]] = []

    def __init__(
        self,
        options: TOptionsValidator,
        enhanced_download_archive: EnhancedDownloadArchive,
        download_ytdl_options: YTDLOptionsBuilder,
        metadata_ytdl_options: YTDLOptionsBuilder,
        overrides: Overrides,
    ):
        super().__init__(
            options=options,
            overrides=overrides,
            enhanced_download_archive=enhanced_download_archive,
        )
        self._download_ytdl_options_builder = download_ytdl_options
        self._metadata_ytdl_options_builder = metadata_ytdl_options

    @abc.abstractmethod
    def download_metadata(self) -> Iterable[Entry]:
        """Gathers metadata of all entries to download"""

    @abc.abstractmethod
    def download(self, entry: Entry) -> Entry:
        """The function to perform the download of all media entries"""

    @final
    def added_plugins(self) -> List[SourcePluginExtension]:
        """Add these plugins from the Downloader to the subscription"""
        return [
            plugin_extension(
                options=self.plugin_options,
                overrides=self.overrides,
                enhanced_download_archive=self._enhanced_download_archive,
            )
            for plugin_extension in self.plugin_extensions
        ]
