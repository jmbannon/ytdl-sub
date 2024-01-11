from typing import Dict
from typing import Optional

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.validators.options import OptionsValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.exceptions import StringFormattingException
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.validators.string_formatter_validators import ListFormatterValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

logger = Logger.get("filter-exclude")


class FilterExcludeOptions(ListFormatterValidator, OptionsValidator):
    """
    Applies a conditional OR on any number of filters comprised of either variables or scripts.
    If any filter evaluates to True, the entry will be excluded.

    :Usage:

    .. code-block:: yaml

       filter_exclude:
         - >-
           { %contains( %lower(title), '#short' ) }
         - >-
           { %contains( %lower(description), '#short' ) }
    """


class FilterExcludePlugin(Plugin[FilterExcludeOptions]):
    plugin_options_type = FilterExcludeOptions

    def __init__(
        self,
        options: FilterExcludeOptions,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        super().__init__(
            options=options,
            overrides=overrides,
            enhanced_download_archive=enhanced_download_archive,
        )
        self._evaluated_map: Dict[str, bool] = {}

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        # Already evaluated in modify_entry_metadata, do not recompute
        if entry.ytdl_uid() in self._evaluated_map:
            return entry

        for formatter in self.plugin_options.list:
            out = ScriptUtils.bool_formatter_output(
                self.overrides.apply_formatter(formatter=formatter, entry=entry)
            )
            if bool(out):
                logger.info(
                    "Filtering '%s' from the filter %s evaluating to True",
                    entry.title,
                    formatter.format_string,
                )
                return None

        return entry

    def modify_entry_metadata(self, entry: Entry) -> Optional[Entry]:
        try:
            output_entry = self.modify_entry(entry=entry)
        except StringFormattingException:
            # If filtering fails at the metadata stage, try again w/no catch in modify_entry
            return entry

        self._evaluated_map[entry.ytdl_uid()] = True
        return output_entry
