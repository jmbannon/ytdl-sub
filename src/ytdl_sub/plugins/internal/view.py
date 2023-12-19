import copy
from typing import Optional

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.validators.options import OptionsDictValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class ViewOptions(OptionsDictValidator):
    """
    INTERNAL PLUGIN. Do not expose in documentation
    """

    _optional_keys = {"_placeholder"}


class ViewPlugin(Plugin[ViewOptions]):
    plugin_options_type = ViewOptions

    _MAX_LINE_WIDTH: int = 80

    def __init__(
        self,
        options: ViewOptions,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        super().__init__(
            options=options,
            overrides=overrides,
            enhanced_download_archive=enhanced_download_archive,
        )
        self._first_entry: Optional[Entry] = None

    @classmethod
    def _truncate_value(cls, value: str) -> str:
        """No new lines and cut off after 80 characters"""
        value = " <newline> ".join(str(value).split("\n"))
        if len(value) > cls._MAX_LINE_WIDTH:
            value = value[:77] + "..."

        return value

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        """Only process the first entry received"""
        if self._first_entry is None:
            self._first_entry = entry
            return entry

        return None

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        """
        Adds all source variables to the entry
        """
        source_var_dict = copy.deepcopy(entry.to_dict())
        for key in source_var_dict.keys():
            source_var_dict[key] = self._truncate_value(source_var_dict[key])

        return FileMetadata.from_dict(title="Source Variables", value_dict=source_var_dict)
