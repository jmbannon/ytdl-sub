import json
import os
import re
import subprocess
from typing import List
from typing import Optional
from typing import Tuple

from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.file_handler import FileMetadata


class Timestamp:

    # Captures the following formats:
    # 0:00 title
    # 00:00 title
    # 1:00:00 title
    # 01:00:00 title
    # where capture group 1 and 2 are the timestamp and title, respectively
    _SPLIT_TIMESTAMP_REGEX = re.compile(r"^((?:\d\d:)?(?:\d:)?(?:\d)?\d:\d\d)$")

    @classmethod
    def _normalize_timestamp_str(cls, timestamp_str: str) -> str:
        match = cls._SPLIT_TIMESTAMP_REGEX.match(timestamp_str)
        if not match:
            raise ValueError(f"Cannot parse youtube timestamp '{timestamp_str}'")

        timestamp = match.group(1)
        match len(timestamp):
            case 4:  # 0:00
                timestamp = f"00:0{timestamp}"
            case 5:  # 00:00
                timestamp = f"00:{timestamp}"
            case 7:  # 0:00:00
                timestamp = f"0{timestamp}"
            case _:
                pass

        assert len(timestamp) == 8
        return timestamp

    def __init__(self, timestamp_sec: int):
        self._timestamp_sec = timestamp_sec

    @property
    def timestamp_sec(self) -> int:
        """
        Returns
        -------
        Timestamp in seconds
        """
        return self._timestamp_sec

    @property
    def _hours_minutes_seconds(self) -> Tuple[int, int, int]:
        seconds = self.timestamp_sec

        hours = int(seconds / 3600)
        seconds -= hours * 3600

        minutes = int(seconds / 60)
        seconds -= minutes * 60

        return hours, minutes, seconds

    @property
    def readable_str(self) -> str:
        """
        Returns
        -------
        The timestamp in '0:SS' format (min trim).
        """
        hours, minutes, seconds = self._hours_minutes_seconds
        if hours:
            return f"{str(hours)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"
        if minutes:
            return f"{str(minutes)}:{str(seconds).zfill(2)}"
        return f"0:{str(seconds).zfill(2)}"

    @property
    def standardized_str(self) -> str:
        """
        Returns
        -------
        The timestamp in 'HH:MM:SS' format
        """
        hours, minutes, seconds = self._hours_minutes_seconds
        return f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}"

    @classmethod
    def from_seconds(cls, timestamp_sec: int) -> "Timestamp":
        """
        Parameters
        ----------
        timestamp_sec
            Timestamp in number of seconds
        """
        return cls(timestamp_sec=timestamp_sec)

    @classmethod
    def from_str(cls, timestamp_str: str) -> "Timestamp":
        """
        Parameters
        ----------
        timestamp_str
            Timestamp in the form of "HH:MM:SS"

        Raises
        ------
        ValueError
            Invalid timestamp string format
        """
        hour_minute_second = cls._normalize_timestamp_str(timestamp_str).split(":")
        if len(hour_minute_second) != 3:
            raise ValueError("Youtube timestamp must be in the form of 'HH:MM:SS'")

        hour, minute, second = tuple(x for x in hour_minute_second)
        try:
            return cls(timestamp_sec=(int(hour) * 3600) + (int(minute) * 60) + int(second))
        except ValueError as cast_exception:
            raise ValueError(
                "Youtube timestamp must be in the form of 'HH:MM:SS'"
            ) from cast_exception


class Chapters:
    """
    Represents a list of (timestamps, titles)
    """

    def __init__(
        self,
        timestamps: List[Timestamp],
        titles: List[str],
    ):
        self.timestamps = timestamps
        self.titles = titles

        for idx in range(len(timestamps) - 1):
            if timestamps[idx].timestamp_sec >= timestamps[idx + 1].timestamp_sec:
                raise ValueError("Timestamps must be in ascending order")

    def contains_any_chapters(self) -> bool:
        """
        Returns
        -------
        True if there are chapters. False otherwise.
        """
        return len(self.timestamps) > 0

    def contains_zero_timestamp(self) -> bool:
        """
        Returns
        -------
        True if the first timestamp starts at 0. False otherwise.
        """
        return self.timestamps[0].timestamp_sec == 0

    def to_file_metadata(self, title: Optional[str] = None) -> FileMetadata:
        """
        Parameters
        ----------
        title
            Optional title

        Returns
        -------
        Chapter metadata in the format of { readable_timestamp_str: title }
        """
        return FileMetadata.from_dict(
            value_dict={ts.readable_str: title for ts, title in zip(self.timestamps, self.titles)},
            title=title,
            sort_dict=False,  # timestamps + titles are already sorted
        )

    @classmethod
    def from_timestamps_file(cls, chapters_file_path: str) -> "Chapters":
        """
        Parameters
        ----------
        chapters_file_path
            Path to file containing chapters

        Raises
        ------
        ValidationException
            File path does not exist or contains invalid formatting
        """
        if not os.path.isfile(chapters_file_path):
            raise ValidationException(
                f"chapter/timestamp file path '{chapters_file_path}' does not exist."
            )

        with open(chapters_file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        timestamps: List[Timestamp] = []
        titles: List[str] = []

        for idx, line in enumerate(lines):
            line_split = line.strip().split(maxsplit=1)

            # Allow the last line to be blank
            if idx == len(lines) - 1 and not line.strip():
                break

            if len(line_split) != 2:
                raise ValidationException(
                    f"Chapter/Timestamp file '{chapters_file_path}' could not parse '{line}': "
                    f"must be in the format of 'HH:MM:SS title"
                )

            timestamp_str, title = tuple(x for x in line_split)

            timestamps.append(Timestamp.from_str(timestamp_str))
            titles.append(title)

        return cls(timestamps=timestamps, titles=titles)

    @classmethod
    def from_embedded_chapters(cls, file_path: str) -> "Chapters":
        """
        Parameters
        ----------
        file_path
            File to read ffmpeg chapter metadata from

        Returns
        -------
        Chapters object
        """
        proc = subprocess.run(
            [
                "ffprobe",
                "-loglevel",
                "quiet",
                "-print_format",
                "json",
                "-show_chapters",
                "--",
                file_path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            encoding="utf-8",
        )

        embedded_chapters = json.loads(proc.stdout)
        timestamps: List[Timestamp] = []
        titles: List[str] = []
        for chapter in embedded_chapters["chapters"]:
            timestamps.append(Timestamp.from_seconds(int(float(chapter["start_time"]))))
            titles.append(chapter["tags"]["title"])

        return Chapters(timestamps=timestamps, titles=titles)

    @classmethod
    def from_entry_chapters(cls, entry: Entry) -> "Chapters":
        """
        Parameters
        ----------
        entry
            Entry with yt-dlp chapter metadata

        Returns
        -------
        Chapters object
        """
        timestamps: List[Timestamp] = []
        titles: List[str] = []

        chapters = {}
        if entry.kwargs_contains("chapters"):
            chapters = entry.kwargs("chapters") or []

        for chapter in chapters:
            timestamps.append(Timestamp.from_seconds(int(float(chapter["start_time"]))))
            titles.append(chapter["title"])

        return Chapters(timestamps=timestamps, titles=titles)
