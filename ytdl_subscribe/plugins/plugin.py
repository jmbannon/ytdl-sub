from abc import ABC
from typing import Generic
from typing import TypeVar
from typing import final

from ytdl_subscribe.config.preset import Overrides
from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.validators.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class PluginValidator(StrictDictValidator):
    """
    Class that defines the parameters to a plugin
    """


PluginValidatorT = TypeVar("PluginValidatorT", bound=PluginValidator)


class Plugin(Generic[PluginValidatorT], ABC):
    """
    Class to define the new plugin functionality
    """

    @final
    def __init__(
        self,
        plugin_options: PluginValidatorT,
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
