from abc import ABC
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Optional


@dataclass
class PlaylistMetadata:
    """
    Metadata for storing playlist information.
    """

    playlist_index: int
    playlist_id: str
    playlist_extractor: str


class BaseEntry(ABC):
    """
    Abstract entry object to represent anything download from ytdl (playlist metadata, media, etc).
    """

    def __init__(self, entry_dict: Dict, working_directory: Optional[str] = None):
        """
        Initialize the entry using ytdl metadata

        Parameters
        ----------
        entry_dict
            Entry metadata
        working_directory
            Optional. Directory that the entry is downloaded to
        """
        self._working_directory = working_directory
        self._kwargs = entry_dict

    def kwargs_contains(self, key: str) -> bool:
        """Returns whether internal kwargs contains the specified key"""
        return key in self._kwargs

    def kwargs(self, key) -> Any:
        """Returns an internal kwarg value supplied from ytdl"""
        if not self.kwargs_contains(key):
            raise KeyError(f"Expected '{key}' in {self.__class__.__name__} but does not exist.")
        return self._kwargs[key]

    def working_directory(self) -> str:
        if self._working_directory is None:
            raise ValueError(
                "Entry working directory is not set when trying to access its download file path"
            )
        return self._working_directory
