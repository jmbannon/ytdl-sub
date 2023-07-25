from abc import ABC
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.config.preset_options import TOptionsValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadArchiver
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class PluginPriority:
    """
    Defines priority for plugins, 0 is highest priority
    """

    # If modify_entry priority is >= to this value, run after split
    MODIFY_ENTRY_AFTER_SPLIT = 10

    # if post_process is >= to this value, run after file_convert
    POST_PROCESS_AFTER_FILE_CONVERT = 10

    MODIFY_ENTRY_FIRST = 0

    def __init__(self, modify_entry: int = 5, post_process: int = 5):
        self.modify_entry = modify_entry
        self.post_process = post_process

    @property
    def modify_entry_after_split(self) -> bool:
        """
        Returns
        -------
        True if the plugin should modify an entry after a potential split. False otherwise.
        """
        return self.modify_entry >= PluginPriority.MODIFY_ENTRY_AFTER_SPLIT


class Plugin(DownloadArchiver, Generic[TOptionsValidator], ABC):
    """
    Class to define the new plugin functionality
    """

    plugin_options_type: Type[TOptionsValidator] = NotImplemented
    priority: PluginPriority = PluginPriority()

    # If the plugin creates multiple entries from a single entry
    is_split_plugin: bool = False

    def __init__(
        self,
        plugin_options: TOptionsValidator,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        DownloadArchiver.__init__(self=self, enhanced_download_archive=enhanced_download_archive)
        self.plugin_options = plugin_options
        self.overrides = overrides
        # TODO pass yaml snake case name in the class somewhere, and use it for the logger
        self._logger = Logger.get(self.__class__.__name__)

    # pylint: disable=no-self-use,unused-argument
    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        ytdl options to enable/disable when downloading entries for this specific plugin
        """

    def split(self, entry: Entry) -> List[Tuple[Entry, FileMetadata]]:
        """
        Very specialized function that takes an entry and creates multiple entries from it.
        Should mark ``is_split_plugin`` on the plugin class.

        Parameters
        ----------
        entry
            Entry to create multiple entries from

        Returns
        -------
        List of entries and metadata created from the source entry
        """
        return []

    def modify_entry_metadata(self, entry: Entry) -> Optional[Entry]:
        """
        After entry metadata has been gathered, perform preprocessing on the metadata

        Parameters
        ----------
        entry
            Entry metadata to modify

        Returns
        -------
        The entry or None, indicating not to download it.
        """
        return entry

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        """
        After each entry is downloaded, modify the entry in some way before sending it to
        post-processing.

        Parameters
        ----------
        entry
            Entry to modify

        Returns
        -------
        The entry or None, indicating not to move it to the output directory
        """
        return entry

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        """
        For each entry downloaded, apply post processing to it.

        Parameters
        ----------
        entry
            Entry to post process

        Returns
        -------
        Optional file metadata for the entry media file.
        """
        return None

    # pylint: enable=no-self-use,unused-argument

    def post_process_subscription(self):
        """
        After all downloaded files have been post-processed, apply a subscription-wide post process
        """
