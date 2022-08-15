import re
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.validators.regex_validator import RegexListValidator
from ytdl_sub.validators.string_select_validator import StringSelectValidator
from ytdl_sub.validators.validators import ListValidator

SPONSORBLOCK_HIGHLIGHT_CATEGORIES: Set[str] = {"poi_highlight"}
SPONSORBLOCK_CATEGORIES: Set[str] = SPONSORBLOCK_HIGHLIGHT_CATEGORIES | {
    "sponsor",
    "intro",
    "outro",
    "selfpromo",
    "preview",
    "filler",
    "interaction",
    "music_offtopic",
}


class SponsorBlockCategoriesValidator(StringSelectValidator):
    _expected_value_type = "sponsorblock category"
    _select_values = {"all"} | SPONSORBLOCK_CATEGORIES


class SponsorBlockCategoryListValidator(ListValidator[SponsorBlockCategoriesValidator]):
    _expected_value_type = "sponsorblock category"
    _inner_list_type = SponsorBlockCategoriesValidator


class ChaptersOptions(PluginOptions):
    """
    Add chapters to video files if they are present. Options to add SponsorBlock chapters and
    remove them or existing chapters.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           chapters:
             sponsorblock_categories:
               - "outro"
               - "selfpromo"
               - "preview"
               - "interaction"
               - "sponsor"
               - "music_offtopic"
               - "intro"
             remove_sponsorblock_categories: "all"
             remove_chapters_regex:
               - "sponsor"

    """

    _optional_keys = {
        "sponsorblock_categories",
        "remove_sponsorblock_categories",
        "remove_chapters_regex",
    }

    def __init__(self, name, value):
        super().__init__(name, value)
        self._sponsorblock_categories = self._validate_key_if_present(
            key="sponsorblock_categories", validator=SponsorBlockCategoryListValidator
        )
        self._remove_sponsorblock_categories = self._validate_key_if_present(
            key="remove_sponsorblock_categories", validator=SponsorBlockCategoryListValidator
        )
        self._remove_chapters_regex = self._validate_key_if_present(
            key="remove_chapters_regex", validator=RegexListValidator
        )

    @property
    def sponsorblock_categories(self) -> Optional[List[str]]:
        if self._sponsorblock_categories:
            return [validator.value for validator in self._sponsorblock_categories.list]
        return None

    @property
    def remove_sponsorblock_categories(self) -> Optional[List[str]]:
        if self._remove_sponsorblock_categories:
            return [validator.value for validator in self._remove_sponsorblock_categories.list]
        return None

    @property
    def remove_chapters_regex(self) -> Optional[List[re.Pattern]]:
        if self._remove_chapters_regex:
            return [validator.compiled_regex for validator in self._remove_chapters_regex.list]
        return None


class ChaptersPlugin(Plugin[ChaptersOptions]):
    plugin_options_type = ChaptersOptions

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        return entry
