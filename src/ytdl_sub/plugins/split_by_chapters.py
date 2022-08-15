import copy
from pathlib import Path
from typing import Optional, List

from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.chapters import Chapters, Timestamp
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.file_handler import FileHandler
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

    def _create_split_entry(
        self, source_entry: Entry, title: str, idx: int, chapters: Chapters
    ) -> Entry:
        """
        Runs ffmpeg to create the split video
        """
        entry_dict = copy.deepcopy(source_entry)
        entry_dict["title"] = title
        entry_dict["playlist_index"] = idx + 1
        entry_dict["playlist_count"] = len(chapters.timestamps)
        entry_dict["id"] = _split_video_uid(source_uid=entry_dict["id"], idx=idx)

        # Remove track and artist since its now split
        if "track" in entry_dict:
            del entry_dict["track"]
        if "artist" in entry_dict:
            del entry_dict["artist"]

        timestamp_begin = chapters.timestamps[idx].readable_str
        timestamp_end = Timestamp(source_entry_dict["duration"]).readable_str
        if idx + 1 < len(chapters.timestamps):
            timestamp_end = chapters.timestamps[idx + 1].readable_str

        metadata = FileMetadata(metadata=f"{timestamp_begin} - {timestamp_end}")
        return (
            YoutubePlaylistVideo(entry_dict=entry_dict, working_directory=self.working_directory),
            metadata,
        )

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        split_entries: List[Entry] = []
        chapters = Chapters.from_embedded_chapters(file_path=entry.get_download_file_path())

        # convert the entry thumbnail early so we do not have to guess the thumbnail extension
        # when copying it
        if not self.is_dry_run:
            convert_download_thumbnail(entry=entry)

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
                FileHandler.copy(
                    src_file_path=entry.get_download_thumbnail_path(),
                    dst_file_path=Path(self.working_directory) / f"{new_uid}.{entry.thumbnail_ext}",
                )

            # Format the split video as a YoutubePlaylistVideo
            split_videos_and_metadata.append(
                self._create_split_video_entry(
                    source_entry_dict=entry_dict, title=title, idx=idx, chapters=chapters
                )
            )

        return split_videos_and_metadata
