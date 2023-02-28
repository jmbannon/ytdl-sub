import json
import re
import subprocess
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.file_handler import FileMetadata


class Timestamp:

    # Captures the following formats:
    # 0:00 title
    # 00:00 title
    # 1:00:00 title
    # 01:00:00 title
    # where capture group 1 and 2 are the timestamp and title, respectively
    TIMESTAMP_REGEX = re.compile(r"((?:\d\d:)?(?:\d:)?(?:\d)?\d:\d\d)")

    @classmethod
    def _normalize_timestamp_str(cls, timestamp_str: str) -> str:
        match = cls.TIMESTAMP_REGEX.match(timestamp_str)
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

    def to_file_metadata_dict(self) -> Dict:
        """
        Returns
        -------
        Metadata dict
        """
        return {ts.readable_str: title for ts, title in zip(self.timestamps, self.titles)}

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
            value_dict=self.to_file_metadata_dict(),
            title=title,
            sort_dict=False,  # timestamps + titles are already sorted
        )

    @classmethod
    def from_string(cls, input_str: str) -> "Chapters":
        """
        From a string (description or comment), try to extract Chapters.
        The scraping logic is simple, if three or more successive lines have timestamps, grab
        as many in succession as possible. Remove the timestamp portion to get the chapter title.

        Parameters
        ----------
        input_str
            String to scrape

        Returns
        -------
        Chapters
            Could be empty
        """
        timestamps: List[Timestamp] = []
        titles: List[str] = []

        for line in input_str.split("\n"):
            # Timestamp captured, store it
            if match := Timestamp.TIMESTAMP_REGEX.search(line):
                timestamp_str = match.group(1)
                timestamps.append(Timestamp.from_str(timestamp_str))

                # Remove timestamp and surrounding whitespace from it
                title_str = re.sub(f"\\s*{re.escape(timestamp_str)}\\s*", " ", line).strip()
                titles.append(title_str)
            elif len(timestamps) >= 3:
                return Chapters(timestamps=timestamps, titles=titles)
            # Timestamp was not stored, if only contained 1, reset
            else:
                timestamps = []
                titles = []

        return Chapters(timestamps=timestamps, titles=titles)

    @classmethod
    def from_embedded_chapters(cls, ffprobe_path: str, file_path: str) -> "Chapters":
        """
        Parameters
        ----------
        ffprobe_path
            Path to ffprobe executable
        file_path
            File to read ffmpeg chapter metadata from

        Returns
        -------
        Chapters object
        """
        proc = subprocess.run(
            [
                ffprobe_path,
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

    @classmethod
    def from_empty(cls) -> "Chapters":
        """
        Initialize empty chapters
        """
        return Chapters(timestamps=[], titles=[])

    def __len__(self) -> int:
        """
        Returns
        -------
        Number of chapters
        """
        return len(self.timestamps)

    def is_empty(self) -> bool:
        """
        Returns
        -------
        True if no chapters. False otherwise.
        """
        return len(self) == 0
