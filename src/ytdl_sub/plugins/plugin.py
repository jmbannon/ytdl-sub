from abc import ABC
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import final

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class PluginOptions(StrictDictValidator):
    """
    Class that defines the parameters to a plugin
    """


PluginOptionsT = TypeVar("PluginOptionsT", bound=PluginOptions)


class Plugin(Generic[PluginOptionsT], ABC):
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
        self.plugin_options = plugin_options
        self.overrides = overrides
        self.__enhanced_download_archive = enhanced_download_archive
        # TODO pass yaml snake case name in the class somewhere, and use it for the logger
        self._logger = Logger.get(self.__class__.__name__)

    @property
    def working_directory(self) -> str:
        return self.__enhanced_download_archive.working_directory

    def save_file(self, file_name: str, entry: Optional[Entry] = None) -> None:
        """
        Saves a file in the working directory to the output directory.

        Parameters
        ----------
        file_name
            Name of the file relative to the working directory
        entry
            Optional. Entry that the file belongs to
        """
        self.__enhanced_download_archive.save_file(
            file_name=file_name, output_file_name=file_name, entry=entry
        )

    def post_process_entry(self, entry: Entry):
        """
        For each file downloaded, apply post processing to it.

        Parameters
        ----------
        entry:
            Entry to post process
        """

    def post_process_subscription(self):
        """
        After all downloaded files have been post-processed, apply a subscription-wide post process
        """
