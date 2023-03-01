import copy
import os.path
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.kwargs import CHAPTERS
from ytdl_sub.entries.variables.kwargs import SPLIT_BY_CHAPTERS_PARENT_ENTRY
from ytdl_sub.entries.variables.kwargs import SPONSORBLOCK_CHAPTERS
from ytdl_sub.entries.variables.kwargs import UID
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.chapters import Chapters
from ytdl_sub.utils.chapters import Timestamp
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.thumbnail import convert_download_thumbnail
from ytdl_sub.validators.string_select_validator import StringSelectValidator


def _split_video_ffmpeg_cmd(
    input_file: str, output_file: str, timestamps: List[Timestamp], idx: int
) -> List[str]:
    timestamp_begin = timestamps[idx].standardized_str
    timestamp_end = timestamps[idx + 1].standardized_str if idx + 1 < len(timestamps) else ""

    cmd = ["-i", input_file, "-ss", timestamp_begin]
    if timestamp_end:
        cmd += ["-to", timestamp_end]
    cmd += ["-vcodec", "copy", "-acodec", "copy", output_file]
    return cmd


def _split_video_uid(source_uid: str, idx: int) -> str:
    return f"{source_uid}___{idx}"


class WhenNoChaptersValidator(StringSelectValidator):
    _expected_value_type_name = "when no chapters option"
    _select_values = {"pass", "drop", "error"}


class SplitByChaptersOptions(PluginOptions):
    """
    Splits a file by chapters into multiple files. Each file becomes its own entry with the
    new source variables ``chapter_title``, ``chapter_title_sanitized``, ``chapter_index``,
    ``chapter_index_padded``, ``chapter_count``.

    If a file has no chapters, and ``when_no_chapters`` is set to "pass", then ``chapter_title`` is
    set to the entry's title and ``chapter_index``, ``chapter_count`` are both set to 1.

    Note that when using this plugin and performing dry-run, it assumes embedded chapters are being
    used with no modifications.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           split_by_chapters:
             when_no_chapters: "pass"
    """

    _required_keys = {"when_no_chapters"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        if isinstance(value, dict):
            value["when_no_chapters"] = value.get("when_no_chapters", "pass")
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)
        self._when_no_chapters = self._validate_key(
            key="when_no_chapters", validator=WhenNoChaptersValidator
        ).value

    def added_source_variables(self) -> List[str]:
        return [
            "chapter_title",
            "chapter_title_sanitized",
            "chapter_index",
            "chapter_index_padded",
            "chapter_count",
        ]

    @property
    def when_no_chapters(self) -> str:
        """
        Behavior to perform when no chapters are present. Supports "pass" (continue processing),
        "drop" (exclude it from output), and "error" (stop processing for everything).
        """
        return self._when_no_chapters


class SplitByChaptersPlugin(Plugin[SplitByChaptersOptions]):
    plugin_options_type = SplitByChaptersOptions
    is_split_plugin = True

    def _create_split_entry(
        self, source_entry: Entry, title: str, idx: int, chapters: Chapters
    ) -> Tuple[Entry, FileMetadata]:
        """
        Runs ffmpeg to create the split video
        """
        entry = copy.deepcopy(source_entry)

        entry.add_variables(
            {
                "chapter_title": title,
                "chapter_title_sanitized": sanitize_filename(title),
                "chapter_index": idx + 1,
                "chapter_index_padded": f"{(idx + 1):02d}",
                "chapter_count": len(chapters.timestamps),
            }
        )

        # pylint: disable=protected-access
        entry.add_kwargs(
            {
                UID: _split_video_uid(source_uid=entry.uid, idx=idx),
                SPLIT_BY_CHAPTERS_PARENT_ENTRY: source_entry._kwargs,
            }
        )

        if entry.kwargs_contains(CHAPTERS):
            del entry._kwargs[CHAPTERS]
        if entry.kwargs_contains(SPONSORBLOCK_CHAPTERS):
            del entry._kwargs[SPONSORBLOCK_CHAPTERS]
        # pylint: enable=protected-access

        timestamp_begin = chapters.timestamps[idx].readable_str
        timestamp_end = Timestamp(entry.kwargs("duration")).readable_str
        if idx + 1 < len(chapters.timestamps):
            timestamp_end = chapters.timestamps[idx + 1].readable_str

        metadata_value_dict = {}
        if self.is_dry_run:
            metadata_value_dict[
                "Warning"
            ] = "Dry-run assumes embedded chapters with no modifications"

        metadata_value_dict["Source Title"] = entry.title
        metadata_value_dict["Segment"] = f"{timestamp_begin} - {timestamp_end}"

        metadata = FileMetadata.from_dict(
            value_dict=metadata_value_dict,
            title="From Chapter Split",
            sort_dict=False,
        )

        return entry, metadata

    def split(self, entry: Entry) -> Optional[List[Tuple[Entry, FileMetadata]]]:
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        split_videos_and_metadata: List[Tuple[Entry, FileMetadata]] = []

        if self.is_dry_run:
            chapters = Chapters.from_entry_chapters(entry=entry)
        else:
            chapters = Chapters.from_embedded_chapters(
                ffprobe_path=FFMPEG.ffprobe_path(),
                file_path=entry.get_download_file_path(),
            )

        # If no chapters, do not split anything
        if not chapters.contains_any_chapters():
            if self.plugin_options.when_no_chapters == "pass":
                entry.add_variables(
                    {
                        "chapter_title": entry.title,
                        "chapter_index": 1,
                        "chapter_index_padded": "01",
                        "chapter_count": 1,
                    }
                )
                return [(entry, FileMetadata())]
            if self.plugin_options.when_no_chapters == "drop":
                return []

            raise ValidationException(
                f"Tried to split '{entry.title}' by chapters but it has no chapters"
            )

        # convert the entry thumbnail early so we do not have to guess the thumbnail extension
        # when copying it. Do not error if it's not found, in case thumbnail_name is not set
        if not self.is_dry_run:
            convert_download_thumbnail(entry=entry, error_if_not_found=False)

        for idx, title in enumerate(chapters.titles):
            new_uid = _split_video_uid(source_uid=entry.uid, idx=idx)

            if not self.is_dry_run:
                # Get the input/output file paths
                input_file = entry.get_download_file_path()
                output_file = str(Path(self.working_directory) / f"{new_uid}.{entry.ext}")

                # Run ffmpeg to create the split the video
                FFMPEG.run(
                    _split_video_ffmpeg_cmd(
                        input_file=input_file,
                        output_file=output_file,
                        timestamps=chapters.timestamps,
                        idx=idx,
                    )
                )

                # Copy the original vid thumbnail to the working directory with the new uid. This so
                # downstream logic thinks this split video has its own thumbnail
                if os.path.isfile(entry.get_download_thumbnail_path()):
                    FileHandler.copy(
                        src_file_path=entry.get_download_thumbnail_path(),
                        dst_file_path=Path(self.working_directory)
                        / f"{new_uid}.{entry.thumbnail_ext}",
                    )

            # Format the split video
            split_videos_and_metadata.append(
                self._create_split_entry(
                    source_entry=entry,
                    title=title,
                    idx=idx,
                    chapters=chapters,
                )
            )

        return split_videos_and_metadata
