from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from ytdl_sub.config.plugin.plugin import SplitPlugin
from ytdl_sub.config.plugin.plugin_operation import PluginOperation
from ytdl_sub.config.validators.options import OptionsDictValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.entry import ytdl_sub_split_by_chapters_parent_uid
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions
from ytdl_sub.utils.chapters import Chapters
from ytdl_sub.utils.chapters import Timestamp
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.validators.string_select_validator import StringSelectValidator

v: VariableDefinitions = VARIABLES


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


class SplitByChaptersOptions(OptionsDictValidator):
    """
    Splits a file by chapters into multiple files. Each file becomes its own entry with the
    new variables

      - ``chapter_title``
      - ``chapter_index``
      - ``chapter_index_padded``
      - ``chapter_count``

    Note that when using this plugin and performing dry-run, it assumes embedded chapters are being
    used with no modifications.

    :Usage:

    .. code-block:: yaml

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

    def added_variables(
        self,
        unresolved_variables: Set[str],
    ) -> Dict[PluginOperation, Set[str]]:
        return {
            PluginOperation.MODIFY_ENTRY: {
                "chapter_title",
                "chapter_index",
                "chapter_index_padded",
                "chapter_count",
            }
        }

    @property
    def when_no_chapters(self) -> str:
        """
        :expected type: String
        :description:
          Behavior to perform when no chapters are present. Supports

            - "pass" (continue processing),
            - "drop" (exclude it from output)
            - "error" (stop processing for everything).

          If a file has no chapters and is set to "pass", then ``chapter_title`` is
          set to the entry's title and ``chapter_index``, ``chapter_count`` are both set to 1.
        """
        return self._when_no_chapters

    def modified_variables(self) -> Dict[PluginOperation, Set[str]]:
        return {
            PluginOperation.MODIFY_ENTRY: {
                v.uid.variable_name,
                ytdl_sub_split_by_chapters_parent_uid.variable_name,
            }
        }


class SplitByChaptersPlugin(SplitPlugin[SplitByChaptersOptions]):
    plugin_options_type = SplitByChaptersOptions

    @classmethod
    def _non_split_entry(cls, entry: Entry) -> Entry:
        entry.add(
            {
                "chapter_title": f"{{ {v.title.variable_name} }}",
                "chapter_index": 1,
                "chapter_index_padded": "01",
                "chapter_count": 1,
                v.uid: entry.uid,
                ytdl_sub_split_by_chapters_parent_uid: entry.uid,
            }
        )
        return entry

    def _create_split_entry(
        self, new_entry: Entry, title: str, idx: int, chapters: Chapters
    ) -> Tuple[Entry, FileMetadata]:
        """
        Runs ffmpeg to create the split video
        """
        new_entry.add(
            {
                "chapter_title": title,
                "chapter_index": idx + 1,
                "chapter_index_padded": f"{(idx + 1):02d}",
                "chapter_count": len(chapters.timestamps),
            }
        )

        timestamp_begin = chapters.timestamps[idx].readable_str
        timestamp_end = Timestamp(new_entry.get(v.duration, int)).readable_str
        if idx + 1 < len(chapters.timestamps):
            timestamp_end = chapters.timestamps[idx + 1].readable_str

        metadata_value_dict = {}
        if self.is_dry_run:
            metadata_value_dict["Warning"] = (
                "Dry-run assumes embedded chapters with no modifications"
            )

        metadata_value_dict["Source Title"] = new_entry.title
        metadata_value_dict["Segment"] = f"{timestamp_begin} - {timestamp_end}"

        metadata = FileMetadata.from_dict(
            value_dict=metadata_value_dict,
            title="From Chapter Split",
            sort_dict=False,
        )

        return new_entry, metadata

    def split(self, entry: Entry) -> Optional[List[Tuple[Entry, FileMetadata]]]:
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        split_videos_and_metadata: List[Tuple[Entry, FileMetadata]] = []
        chapters = Chapters.from_entry_chapters(entry=entry)

        # If no chapters, do not split anything
        if not chapters.contains_any_chapters():
            if self.plugin_options.when_no_chapters == "pass":
                # Modify the entry t
                return [(self._non_split_entry(entry), FileMetadata())]

            if self.plugin_options.when_no_chapters == "drop":
                return []

            raise ValidationException(
                f"Tried to split '{entry.title}' by chapters but it has no chapters"
            )

        for idx, title in enumerate(chapters.titles):
            new_entry = Entry.create_split_entry(
                entry=entry, new_uid=_split_video_uid(source_uid=entry.uid, idx=idx)
            )

            if not self.is_dry_run:
                # Run ffmpeg to create the split the video
                FFMPEG.run(
                    _split_video_ffmpeg_cmd(
                        input_file=entry.get_download_file_path(),
                        output_file=new_entry.get_download_file_path(),
                        timestamps=chapters.timestamps,
                        idx=idx,
                    )
                )

                # Copy the original vid thumbnail to the working directory with the new uid. This so
                # downstream logic thinks this split video has its own thumbnail
                if entry.is_thumbnail_downloaded():
                    FileHandler.copy(
                        src_file_path=entry.get_download_thumbnail_path(),
                        dst_file_path=new_entry.get_download_thumbnail_path(),
                    )

            # Format the split video
            split_videos_and_metadata.append(
                self._create_split_entry(
                    new_entry=new_entry,
                    title=title,
                    idx=idx,
                    chapters=chapters,
                )
            )

        return split_videos_and_metadata
