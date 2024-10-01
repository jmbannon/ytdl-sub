from abc import ABC
from abc import abstractmethod
from functools import cached_property
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.validators.options import OptionsValidatorT
from ytdl_sub.config.validators.options import ToggleableOptionsDictValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadArchiver
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

# pylint: disable=unused-argument


class BasePlugin(DownloadArchiver, Generic[OptionsValidatorT], ABC):
    """
    Shared code amongst all SourcePlugins (downloaders) and Plugins (post-download modification)
    """

    plugin_options_type: Type[OptionsValidatorT]

    def __init__(
        self,
        options: OptionsValidatorT,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        DownloadArchiver.__init__(self=self, enhanced_download_archive=enhanced_download_archive)
        self.plugin_options = options
        self.overrides = overrides


class Plugin(BasePlugin[OptionsValidatorT], Generic[OptionsValidatorT], ABC):
    """
    Class to define the new plugin functionality
    """

    @cached_property
    def is_enabled(self) -> bool:
        """
        Returns True if enabled, False if disabled.
        """
        if isinstance(self.plugin_options, ToggleableOptionsDictValidator):
            return ScriptUtils.bool_formatter_output(
                self.overrides.apply_formatter(self.plugin_options.enable)
            )
        return True

    def ytdl_options_match_filters(self) -> Tuple[List[str], List[str]]:
        """
        Returns
        -------
        Tuple of match-filters to apply, first one being non-breaking, second breaking
        """
        return [], []

    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        ytdl options to enable/disable when downloading entries for this specific plugin
        """

    def initialize_subscription(self) -> bool:
        """
        Before any downloading begins, perform initialization before the subscription runs.
        Returns true if this subscription should run, false otherwise.
        """
        return True

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

    def post_process_subscription(self):
        """
        After all downloaded files have been post-processed, apply a subscription-wide post process
        """


class SplitPlugin(Plugin[OptionsValidatorT], Generic[OptionsValidatorT], ABC):
    """
    Plugin that splits entries into zero or more entries
    """

    @abstractmethod
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
