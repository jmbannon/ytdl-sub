import re
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from sanitize_filename import sanitize


class EntryFormatter:
    """
    Ensures user-created formatter strings are valid
    """

    FIELDS_VALIDATOR = re.compile(r"{([a-z_]+?)}")

    def __init__(self, format_string: str):
        self.format_string = format_string
        self._error_prefix = f"Format string '{self.format_string}' is invalid:"

    def parse(self) -> List[str]:
        """
        Returns
        -------
        List of fields to format
        """
        open_bracket_count = self.format_string.count("{")
        close_bracket_count = self.format_string.count("}")

        if open_bracket_count != close_bracket_count:
            raise ValueError(
                f"{self._error_prefix} Brackets are reserved for {{variable_names}} "
                f"and should contain a single open and close bracket."
            )

        parsed_fields = re.findall(EntryFormatter.FIELDS_VALIDATOR, self.format_string)

        if len(parsed_fields) != open_bracket_count:
            raise ValueError(
                f"{self._error_prefix} {{variable_names}} should only contain "
                f"lowercase letters and underscores with a single open and close bracket."
            )

        return sorted(parsed_fields)


class Entry:
    """
    Entry object to represent a single media object returned from yt-dlp.
    """

    def __init__(self, **kwargs):
        """
        Initialize the entry using ytdl metadata
        """
        self._kwargs = kwargs

    def kwargs_contains(self, key: str) -> bool:
        """Returns whether internal kwargs contains the specified key"""
        return key in self._kwargs

    def kwargs(self, key) -> Any:
        """Returns an internal kwarg value supplied from ytdl"""
        if not self.kwargs_contains(key):
            raise KeyError(
                f"Expected '{key}' in {self.__class__.__name__} but does not exist."
            )
        return self._kwargs[key]

    @property
    def uid(self) -> str:
        """Returns the entry's unique id"""
        return self.kwargs("id")

    @property
    def title(self) -> str:
        """Returns the entry's title"""
        return self.kwargs("title")

    @property
    def sanitized_title(self) -> str:
        """Returns the entry's sanitized title"""
        return sanitize(self.title)

    @property
    def ext(self) -> str:
        """Returns the entry's file extension"""
        return self.kwargs("ext")

    @property
    def upload_date(self) -> str:
        """Returns the entry's upload date"""
        return self.kwargs("upload_date")

    @property
    def upload_year(self) -> int:
        """Returns the entry's upload year"""
        return int(self.upload_date[:4])

    @property
    def thumbnail(self) -> str:
        """Returns the entry's thumbnail url"""
        return self.kwargs("thumbnail")

    @property
    def thumbnail_ext(self) -> str:
        """Returns the entry's thumbnail extension"""
        return self.thumbnail.split(".")[-1]

    @property
    def download_file_name(self) -> str:
        """Returns the entry's file name when downloaded locally"""
        return f"{self.uid}.{self.ext}"

    def file_path(self, relative_directory: str):
        """Returns the entry's file path with respect to the relative directory"""
        return str(Path(relative_directory) / self.download_file_name)

    def to_dict(self) -> Dict:
        """Returns the entry's values as a dictionary"""
        return {
            "uid": self.uid,
            "title": self.title,
            "sanitized_title": self.sanitized_title,
            "ext": self.ext,
            "upload_date": self.upload_date,
            "upload_year": self.upload_year,
            "thumbnail": self.thumbnail,
            "thumbnail_ext": self.thumbnail_ext,
        }

    def apply_formatter(
        self, format_string: str, overrides: Optional[Dict] = None
    ) -> str:
        """
        Perform a string format on the given format string, using the entry's dict for format
        values. The override dict will overwrite any values within the entry's dict.
        """
        entry_dict = self.to_dict()
        if overrides:
            entry_dict = dict(entry_dict, **overrides)

        field_names = EntryFormatter(format_string).parse()

        for field_name in field_names:
            if field_name not in entry_dict:
                available_fields = ", ".join(sorted(entry_dict.keys()))
                raise ValueError(
                    f"Format variable '{field_name}' does not exist "
                    f"for {self.__class__.__name__}. Available fields: {available_fields}"
                )

        return format_string.format(**entry_dict)
