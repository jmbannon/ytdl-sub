import subprocess
import tempfile
from typing import Dict
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


def add_metadata(
    file_path: str,
    metadata: Optional[Dict[str, str]],
    chapters: Optional[Chapters],
) -> None:

    if not metadata and not chapters:
        return

    lines = [";FFMETADATA1"]

    if metadata:
        for key, value in metadata.items():
            lines.append(f"{_ffmpeg_metadata_escape(key)}={_ffmpeg_metadata_escape(value)}")

    if chapters:
        if not chapters.contains_zero_timestamp():
            raise ValueError("Chapters must contain a zero timestamp")

        for idx in range(len(chapters.timestamps)):
            start = chapters.timestamps[idx].timestamp_sec
            end = (
                chapters.timestamps[idx + 1].timestamp_sec
                if idx < len(chapters.timestamps) - 1
                else chapters.duration
            )

            lines.append("")
            lines.append("[CHAPTER]")
            lines.append("TIMEBASE=1")
            lines.append(f"START={start}")
            lines.append(f"END={end}")
            lines.append(f"title={_ffmpeg_metadata_escape(chapters.titles[idx])}")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8") as tmp_file:
        tmp_file.writelines(lines)
        tmp_file.flush()

        yield tmp_file.name

    return None
