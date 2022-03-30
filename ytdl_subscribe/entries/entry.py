from string import Formatter
from typing import Any, Dict, Optional

from sanitize_filename import sanitize


class Entry(object):
    """
    Entry object to represent a single media object returned from yt-dlp.
    """

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def kwargs(self, key) -> Any:
        if key not in self._kwargs:
            raise KeyError(
                f"Expected '{key}' in {self.__class__.__name__} but does not exist."
            )
        return self._kwargs[key]

    @property
    def uid(self) -> str:
        return self.kwargs("id")

    @property
    def title(self) -> str:
        return self.kwargs("title")

    @property
    def sanitized_title(self) -> str:
        return sanitize(self.title)

    @property
    def ext(self) -> str:
        return self.kwargs("ext")

    @property
    def download_file_name(self) -> str:
        return f"{self.uid}.{self.ext}"

    def file_path(self, relative_directory: str):
        return f"{relative_directory}/{self.download_file_name}"

    def to_dict(self) -> Dict:
        return {
            "uid": self.uid,
            "title": self.title,
            "sanitized_title": self.sanitized_title,
            "ext": self.ext,
        }

    def apply_formatter(self, format_string: str, overrides: Optional[Dict]) -> str:
        entry_dict = self.to_dict()
        if overrides:
            entry_dict = dict(entry_dict, **overrides)

        field_names = [
            fname for _, fname, _, _ in Formatter().parse(format_string) if fname
        ]
        for fname in field_names:
            if fname not in entry_dict:
                raise KeyError(
                    f"Format variable '{fname}' does not exist for {self.__class__.__name__}."
                )

        return format_string.format(**entry_dict)
