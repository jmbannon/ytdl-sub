import collections
import re
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.kwargs import COMMENTS
from ytdl_sub.entries.variables.kwargs import YTDL_SUB_CUSTOM_CHAPTERS
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.chapters import Chapters
from ytdl_sub.utils.ffmpeg import set_ffmpeg_metadata_chapters
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
        return entry.kwargs("chapters") or []
    return []


def _sponsorblock_chapters(entry: Entry) -> List[Dict]:
    if entry.kwargs_contains("sponsorblock_chapters"):
        return entry.kwargs("sponsorblock_chapters") or []
    return []


def _contains_any_chapters(entry: Entry) -> bool:
    return len(_chapters(entry)) > 0 or len(_sponsorblock_chapters(entry)) > 0


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

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           chapters:
             # Embedded Chapter Fields
             embed_chapters: True
             allow_chapters_from_comments: False
             remove_chapters_regex:
               - "Intro"
               - "Outro"

             # Sponsorblock Fields
             sponsorblock_categories:
               - "outro"
               - "selfpromo"
               - "preview"
               - "interaction"
               - "sponsor"
               - "music_offtopic"
               - "intro"
             remove_sponsorblock_categories: "all"
             force_key_frames: False

    """

    _optional_keys = {
        "embed_chapters",
        "allow_chapters_from_comments",
        "sponsorblock_categories",
        "remove_sponsorblock_categories",
        "remove_chapters_regex",
        "force_key_frames",
    }

    def __init__(self, name, value):
        super().__init__(name, value)
        self._embed_chapters = self._validate_key_if_present(
            key="embed_chapters", validator=BoolValidator, default=True
        ).value
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
        self._allow_chapters_from_comments = self._validate_key_if_present(
            key="allow_chapters_from_comments", validator=BoolValidator, default=False
        ).value

        if self._remove_sponsorblock_categories and not self._sponsorblock_categories:
            raise self._validation_exception(
                "Must specify sponsorblock_categories if you are going to remove any of them"
            )

        if self._remove_sponsorblock_categories and self._allow_chapters_from_comments:
            raise self._validation_exception(
                "Cannot remove sponsorblock categories and embed chapters from comments"
            )

    @property
    def embed_chapters(self) -> Optional[bool]:
        """
        Optional. Embed chapters into the file. Defaults to True.
        """
        return self._embed_chapters

    @property
    def allow_chapters_from_comments(self) -> bool:
        """
        Optional. If chapters do not exist in the video/description itself, attempt to scrape
        comments to find the chapters. Defaults to False.
        """
        return self._allow_chapters_from_comments

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

        if self.plugin_options.embed_chapters:
            builder.add(
                {
                    "postprocessors": [
                        {"key": "FFmpegMetadata", "add_chapters": True, "add_metadata": False}
                    ]
                }
            )

        if self.plugin_options.allow_chapters_from_comments:
            builder.add({"getcomments": True})

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

            if self.plugin_options.embed_chapters:
                builder.add(
                    {
                        # re-add chapters
                        "postprocessors": [
                            remove_chapters_post_processor,
                            {"key": "FFmpegMetadata", "add_chapters": True, "add_metadata": False},
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

    def modify_entry(self, entry: Entry) -> Entry:
        """
        Parameters
        ----------
        entry
            Entry to add custom chapters using timestamps if present

        Returns
        -------
        entry
        """
        chapters = Chapters.from_empty()

        if not _contains_any_chapters(entry) and self.plugin_options.allow_chapters_from_comments:
            for comment in entry.kwargs_get(COMMENTS, []):
                chapters = Chapters.from_string(comment.get("text", ""))
                if not chapters.is_empty():
                    break

        if not chapters.is_empty():
            entry.add_kwargs({YTDL_SUB_CUSTOM_CHAPTERS: chapters.to_file_metadata_dict()})

            if not self.is_dry_run:
                set_ffmpeg_metadata_chapters(
                    file_path=entry.get_download_file_path(),
                    chapters=chapters,
                    file_duration_sec=entry.kwargs("duration"),
                )

        return entry

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
        if custom_chapters_metadata := entry.kwargs_get(YTDL_SUB_CUSTOM_CHAPTERS):
            title: str = "Chapters from comments"
            return FileMetadata.from_dict(
                value_dict=custom_chapters_metadata,
                title=title,
                sort_dict=False,  # timestamps + titles are already sorted
            )

        if self.plugin_options.embed_chapters:
            metadata_dict = {}
            removed_chapters = self._get_removed_chapters(entry)
            removed_sponsorblock = self._get_removed_sponsorblock_category_counts(entry)

            # If no chapters are on the entry, do not report any embedded chapters
            if not _contains_any_chapters(entry):
                return None

            if removed_chapters:
                metadata_dict["Removed Chapter(s)"] = ", ".join(removed_chapters)
            if removed_sponsorblock:
                metadata_dict["Removed SponsorBlock Category Count(s)"] = removed_sponsorblock

            # TODO: check if file actually has embedded chapters
            return FileMetadata.from_dict(
                value_dict=metadata_dict, title="Embedded Chapters", sort_dict=False
            )

        return None
