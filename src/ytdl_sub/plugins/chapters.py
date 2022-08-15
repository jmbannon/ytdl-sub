import collections
import re
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.validators.regex_validator import RegexListValidator
from ytdl_sub.validators.string_select_validator import StringSelectValidator
from ytdl_sub.validators.validators import BoolValidator
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


def _chapters(entry: Entry) -> List[Dict]:
    if entry.kwargs_contains("chapters"):
        return entry.kwargs("chapters")
    return []


def _sponsorblock_chapters(entry: Entry) -> List[Dict]:
    if entry.kwargs_contains("sponsorblock_chapters"):
        return entry.kwargs("sponsorblock_chapters")
    return []


class SponsorBlockCategoriesValidator(StringSelectValidator):
    _expected_value_type_name = "sponsorblock category"
    _select_values = {"all"} | SPONSORBLOCK_CATEGORIES


class SponsorBlockCategoryListValidator(ListValidator[SponsorBlockCategoriesValidator]):
    _expected_value_type_name = "sponsorblock category"
    _inner_list_type = SponsorBlockCategoriesValidator


class ChaptersOptions(PluginOptions):
    """
    Embeds chapters to video files if they are present. Additional options to add SponsorBlock
    chapters and remove specific ones. Can also remove chapters using regex.

    Note that at this time, chapter removal with regex will not work with chapters added via
    timestamp file.

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
               - "Intro"
               - "Outro"
             force_key_frames: False

    To simply embed chapters from the entry file and nothing more, specify the following:

    .. code-block:: yaml

       presets:
         my_example_preset:
           chapters:
    """

    _optional_keys = {
        "sponsorblock_categories",
        "remove_sponsorblock_categories",
        "remove_chapters_regex",
        "force_key_frames",
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
        self._force_key_frames = self._validate_key_if_present(
            key="force_key_frames", validator=BoolValidator, default=False
        ).value

        if self._remove_sponsorblock_categories and not self._sponsorblock_categories:
            raise self._validation_exception(
                "Must specify sponsorblock_categories if you are going to remove any of them"
            )

    @property
    def sponsorblock_categories(self) -> Optional[List[str]]:
        """
        Optional. List of SponsorBlock categories to embed as chapters. Supports "sponsor",
        "intro", "outro", "selfpromo", "preview", "filler", "interaction", "music_offtopic",
        "poi_highlight", or "all" to include all categories.
        """
        if self._sponsorblock_categories:
            category_list = [validator.value for validator in self._sponsorblock_categories.list]
            if "all" in category_list:
                return list(SPONSORBLOCK_CATEGORIES)
            return category_list
        return None

    @property
    def remove_sponsorblock_categories(self) -> Optional[List[str]]:
        """
        Optional. List of SponsorBlock categories to remove from the output file. Can only remove
        categories that are specified in ``sponsorblock_categories`` or "all", which removes
        everything specified in ``sponsorblock_categories``.
        """
        if self._remove_sponsorblock_categories:
            category_list = [
                validator.value for validator in self._remove_sponsorblock_categories.list
            ]
            if "all" in category_list:
                return list(set(self.sponsorblock_categories) - SPONSORBLOCK_HIGHLIGHT_CATEGORIES)
            return category_list
        return None

    @property
    def remove_chapters_regex(self) -> Optional[List[re.Pattern]]:
        """
        Optional. List of regex patterns to match chapter titles against and remove them from the
        entry.
        """
        if self._remove_chapters_regex:
            return [validator.compiled_regex for validator in self._remove_chapters_regex.list]
        return None

    @property
    def force_key_frames(self) -> bool:
        """
        Optional. Force keyframes at cuts when removing sections. This is slow due to needing a
        re-encode, but the resulting video may have fewer artifacts around the cuts. Defaults to
        False.
        """
        return self._force_key_frames


class ChaptersPlugin(Plugin[ChaptersOptions]):
    plugin_options_type = ChaptersOptions

    @property
    def _is_removing_chapters(self) -> bool:
        return (
            self.plugin_options.remove_chapters_regex is not None
            or self.plugin_options.remove_sponsorblock_categories is not None
        )

    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        YTDL options to embed chapters, add/remove SponsorBlock segments, remove chapters via regex
        """
        builder = YTDLOptionsBuilder()
        if self.plugin_options.sponsorblock_categories:
            builder.add(
                {
                    "postprocessors": [
                        {
                            "key": "SponsorBlock",
                            "when": "pre_process",
                            "categories": self.plugin_options.sponsorblock_categories,
                        },
                        {"key": "ModifyChapters"},
                    ]
                }
            )

        # Always add chapters
        builder.add({"postprocessors": [{"key": "FFmpegMetadata", "add_chapters": True}]})

        if self._is_removing_chapters:
            remove_chapters_post_processor = {
                "key": "ModifyChapters",
                "force_keyframes": self.plugin_options.force_key_frames,
            }
            if self.plugin_options.remove_sponsorblock_categories is not None:
                remove_chapters_post_processor[
                    "remove_sponsor_segments"
                ] = self.plugin_options.remove_sponsorblock_categories
            if self.plugin_options.remove_chapters_regex is not None:
                remove_chapters_post_processor[
                    "remove_chapters_patterns"
                ] = self.plugin_options.remove_chapters_regex

            builder.add(
                {
                    "postprocessors": [
                        remove_chapters_post_processor,
                        {"key": "FFmpegMetadata", "add_chapters": True},  # re-add chapters
                    ]
                }
            )

        return builder.to_dict()

    def _get_removed_chapters(self, entry: Entry) -> List[str]:
        removed_chapters: List[str] = []
        for pattern in self.plugin_options.remove_chapters_regex or []:
            for chapter in _chapters(entry):
                if pattern.search(chapter["title"]):
                    removed_chapters.append(chapter["title"])
        return removed_chapters

    def _get_removed_sponsorblock_category_counts(self, entry: Entry) -> Dict:
        removed_category_counts = collections.Counter()
        for category in self.plugin_options.remove_sponsorblock_categories or []:
            for chapter in _sponsorblock_chapters(entry):
                if chapter["category"] == category:
                    removed_category_counts.update({chapter["title"]: 1})

        # To make this reproducible, we must sort categories with equal counts by name,
        return dict(
            sorted(
                removed_category_counts.most_common(),
                key=lambda name_count: (-name_count[1], name_count[0]),
            )
        )

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        """
        Parameters
        ----------
        entry:
            Entry with possibly removed chapters

        Returns
        -------
        FileMetadata outlining which chapters/SponsorBlock segments got removed
        """
        metadata_dict = {}
        removed_chapters = self._get_removed_chapters(entry)
        removed_sponsorblock = self._get_removed_sponsorblock_category_counts(entry)

        if removed_chapters:
            metadata_dict["Removed Chapter(s)"] = ", ".join(removed_chapters)
        if removed_sponsorblock:
            metadata_dict["Removed SponsorBlock Category Count(s)"] = removed_sponsorblock

        return FileMetadata.from_dict(
            value_dict=metadata_dict, title="Embedded Chapters", sort_dict=False
        )
