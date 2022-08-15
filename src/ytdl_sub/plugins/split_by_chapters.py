from typing import Dict
from typing import Optional

from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.validators.string_select_validator import StringSelectValidator


class WhenNoChaptersValidator(StringSelectValidator):
    _expected_value_type = "when no chapters option"
    _select_values = {"pass", "drop", "error"}


class SplitByChaptersOptions(PluginOptions):
    """
    Splits a file by chapters into multiple files. Each file becomes its own entry with ``title``
    set to its chapter name, and is processed separately by other plugins.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           split_by_chapters:
             when_no_chapters: "pass"  # "drop"/"error"
    """

    _required_keys = {"when_no_chapters"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._when_no_chapters = self._validate_key(
            key="when_no_chapters", validator=WhenNoChaptersValidator
        ).value

    @property
    def when_no_chapters(self) -> str:
        """
        Behavior to perform when no chapters are present. Supports "pass" (continue processing),
        "drop" (exclude it from output), and "error" (stop processing for everything).
        """
        return self._when_no_chapters


class SplitByChaptersPlugin(Plugin[SplitByChaptersOptions]):
    plugin_options_type = SplitByChaptersOptions

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        return entry
