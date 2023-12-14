import re
from typing import Dict
from typing import List
from typing import Tuple

from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.entry import ytdl_sub_chapters_from_comments
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions
from ytdl_sub.utils.file_handler import FileMetadata

v: VariableDefinitions = VARIABLES


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

    def to_yt_dlp_chapter_metadata(self) -> List[Dict[str, str | float]]:
        """
        Returns
        -------
        Metadata dict
        """
        return [
            {"start_time": ts.timestamp_sec, "title": title}
            for ts, title in zip(self.timestamps, self.titles)
        ]

    def to_file_metadata_dict(self) -> Dict:
        """
        Returns
        -------
        Metadata dict
        """
        return {ts.readable_str: title for ts, title in zip(self.timestamps, self.titles)}

    def to_file_metadata(self, title: str) -> FileMetadata:
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

        # Try to accumulate chapters by parsing lines individually
        for line in input_str.split("\n"):
            # Timestamp captured, store it
            if match := Timestamp.TIMESTAMP_REGEX.search(line):
                timestamp_str = match.group(1)
                timestamps.append(Timestamp.from_str(timestamp_str))

                # Remove timestamp and surrounding whitespace from it
                title_str = re.sub(f"\\s*{re.escape(timestamp_str)}\\s*", " ", line).strip()
                titles.append(title_str)

        # If more than 3 timestamps were parsed, return it
        if len(timestamps) >= 3:
            return Chapters(timestamps=timestamps, titles=titles)

        # Otherwise return empty chapters
        return cls.from_empty()

    @classmethod
    def from_yt_dlp_chapters(cls, chapters: List[Dict[str, str | float]]):
        """
        Create a Chapters object from the raw ``chapters`` metadata returned in an info.json
        """
        timestamps: List[Timestamp] = []
        titles: List[str] = []

        for chapter in chapters:
            timestamps.append(Timestamp.from_seconds(int(float(chapter["start_time"]))))
            titles.append(chapter["title"])

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
        if chapters := (
            entry.try_get(ytdl_sub_chapters_from_comments, list) or entry.get(v.chapters, list)
        ):
            return cls.from_yt_dlp_chapters(chapters)

        return cls.from_empty()

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
