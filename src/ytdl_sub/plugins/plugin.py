from abc import ABC
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import final

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadArchiver
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class PluginOptions(StrictDictValidator):
    """
    Class that defines the parameters to a plugin
    """


PluginOptionsT = TypeVar("PluginOptionsT", bound=PluginOptions)


class Plugin(DownloadArchiver, Generic[PluginOptionsT], ABC):
    """
    Class to define the new plugin functionality
    """

    plugin_options_type: Type[PluginOptionsT] = NotImplemented

    @final
    def __init__(
        self,
        plugin_options: PluginOptionsT,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        DownloadArchiver.__init__(self=self, enhanced_download_archive=enhanced_download_archive)
        self.plugin_options = plugin_options
        self.overrides = overrides
        # TODO pass yaml snake case name in the class somewhere, and use it for the logger
        self._logger = Logger.get(self.__class__.__name__)

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        """
        For each file downloaded, apply post processing to it.

        Parameters
        ----------
        entry:
            Entry to post process

        Returns
        -------
        Optional file metadata for the entry media file.
        """

    def post_process_subscription(self):
        """
        After all downloaded files have been post-processed, apply a subscription-wide post process
        """
