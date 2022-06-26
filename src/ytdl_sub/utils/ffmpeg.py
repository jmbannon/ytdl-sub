import shutil
import subprocess
import tempfile
from typing import List
from typing import Optional

from ytdl_sub.utils.chapters import Chapters
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.logger import Logger

logger = Logger.get(name="ffmpeg")

_FFMPEG_METADATA_SPECIAL_CHARS = ["=", ";", "#", "\n", "\\"]


def _ffmpeg_metadata_escape(str_to_escape: str) -> str:
    # backslash at the end of the list is intentional
    for special_char in _FFMPEG_METADATA_SPECIAL_CHARS:
        str_to_escape.replace(special_char, f"\\{special_char}")

    return str_to_escape


class FFMPEG:
    @classmethod
    def _ensure_installed(cls):
        try:
            subprocess.check_output(["which", "ffmpeg"])
        except subprocess.CalledProcessError as subprocess_error:
            raise ValidationException(
                "Trying to use a feature which requires ffmpeg, but it cannot be found"
            ) from subprocess_error

    @classmethod
    def run(cls, ffmpeg_args: List[str]) -> None:
        """
        Runs an ffmpeg command. Should not include 'ffmpeg' as the beginning argument.

        Parameters
        ----------
        ffmpeg_args:
            Arguments to pass to ffmpeg. Each one will be separated by a space.
        """
        cls._ensure_installed()

        cmd = ["ffmpeg"]
        cmd.extend(ffmpeg_args)
        logger.debug("Running %s", " ".join(cmd))
        subprocess.run(cmd, check=True)


def _create_metadata_chapter_entry(start_sec: int, end_sec: int, title: str) -> List[str]:
    return [
        "",
        "[CHAPTER]",
        "TIMEBASE=1/1000",
        f"START={start_sec * 1000}",
        f"END={end_sec * 1000}",
        f"title={_ffmpeg_metadata_escape(title)}",
    ]


def _create_metadata_chapters(chapters: Chapters, file_duration_sec: int) -> List[str]:
    lines: List[str] = []

    if not chapters.contains_zero_timestamp():
        lines += _create_metadata_chapter_entry(
            start_sec=0,
            end_sec=chapters.timestamps[0].timestamp_sec,
            title="Intro",  # TODO: make this configurable
        )

    for idx in range(len(chapters.timestamps) - 1):
        lines += _create_metadata_chapter_entry(
            start_sec=chapters.timestamps[idx].timestamp_sec,
            end_sec=chapters.timestamps[idx + 1].timestamp_sec,
            title=chapters.titles[idx],
        )

    # Add the last chapter using the file duration
    lines += _create_metadata_chapter_entry(
        start_sec=chapters.timestamps[-1].timestamp_sec,
        end_sec=file_duration_sec,
        title=chapters.titles[-1],
    )

    return lines


def add_ffmpeg_metadata(
    file_path: str, chapters: Optional[Chapters], file_duration_sec: int
) -> None:
    """
    Adds ffmetadata to a file. TODO: support more than just chapters

    Parameters
    ----------
    file_path
        Full path to the file to add metadata to
    chapters
        Chapters to embed in the file. If a chapter for 0:00 does not exist, one is created
    file_duration_sec
        Length of the file in seconds
    """
    lines = [";FFMETADATA1"]

    if chapters:
        lines += _create_metadata_chapters(chapters=chapters, file_duration_sec=file_duration_sec)

    file_path_ext = file_path.split(".")[-1]
    output_file_path = f"{file_path}.out.{file_path_ext}"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8") as metadata_file:
        metadata_file.write("\n".join(lines))
        metadata_file.flush()

        FFMPEG.run(
            [
                "-i",
                file_path,
                "-i",
                metadata_file.name,
                "-map_metadata",
                "1",
                "-bitexact",  # for reproducibility
                "-codec",
                "copy",
                output_file_path,
            ]
        )

        shutil.move(src=output_file_path, dst=file_path)
