from abc import ABC
from typing import Generic
from typing import Type
from typing import TypeVar
from typing import final

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.entries.entry import Entry
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
        output_directory: str,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        self.plugin_options = plugin_options
        self.output_directory = output_directory
        self.overrides = overrides
        self.__enhanced_download_archive = enhanced_download_archive

    @final
    def archive_entry_file_name(self, entry: Entry, relative_file_path: str) -> None:
        """
        Adds an entry and a file name that belongs to it into the archive mapping.

        Parameters
        ----------
        entry:
            Optional. The entry the file belongs to
        relative_file_path:
            The name of the file path relative to the output directory
        """
        self.__enhanced_download_archive.mapping.add_entry(
            entry=entry, entry_file_path=relative_file_path
        )

    def post_process_entry(self, entry: Entry):
        """
        For each file downloaded, apply post processing to it.

        Parameters
        ----------
        entry: Entry to post process
        """

    def post_process_subscription(self):
        """
        After all downloaded files have been post-processed, apply a subscription-wide post process
        """
