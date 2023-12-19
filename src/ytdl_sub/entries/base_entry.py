# pylint: disable=protected-access
from abc import ABC
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import final

from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions

v: VariableDefinitions = VARIABLES

TBaseEntry = TypeVar("TBaseEntry", bound="BaseEntry")


class BaseEntry(ABC):
    """
    Abstract entry object to represent anything download from ytdl (playlist metadata, media, etc).
    """

    def __init__(self, entry_dict: Dict, working_directory: str):
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

    @property
    def uid(self) -> str:
        """
        Returns
        -------
        str
            The entry's unique ID
        """
        return str(self._kwargs[v.uid.metadata_key])

    @property
    def download_archive_extractor(self) -> str:
        """
        The extractor name used in yt-dlp download archives
        """
        # pylint: disable=line-too-long
        # Taken from https://github.com/yt-dlp/yt-dlp/blob/e6ab678e36c40ded0aae305bbb866cdab554d417/yt_dlp/YoutubeDL.py#L3514
        # pylint: enable=line-too-long
        return str(
            self._kwargs_get(v.extractor_key.metadata_key)
            or self._kwargs_get(v.ie_key.metadata_key)
            or "NO_EXTRACTOR"
        ).lower()

    @property
    def title(self) -> str:
        """
        The title of the entry. If a title does not exist, returns its unique ID.
        """
        return self._kwargs_get(v.title.metadata_key, self.uid)

    @property
    def webpage_url(self) -> str:
        """
        The url to the webpage.
        """
        return self._kwargs[v.webpage_url.metadata_key]

    @property
    def info_json_ext(self) -> str:
        """The "info.json" extension"""
        return "info.json"

    @property
    def uploader_id(self) -> str:
        """
        The uploader id if it exists, otherwise return the unique ID.
        """
        return self._kwargs_get(v.uploader_id.metadata_key, self.uid)

    def _kwargs_get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Dict get on kwargs
        """
        if (out := self._kwargs.get(key)) is None:
            return default
        return out

    def working_directory(self) -> str:
        """
        Returns
        -------
        The working directory
        """
        return self._working_directory

    def add_kwargs(self, variables_to_add: Dict[str, Any]) -> "BaseEntry":
        """
        Adds variables to kwargs. Use with caution since yt-dlp data can be overwritten.
        Plugins should use ``add_variables``.

        Parameters
        ----------
        variables_to_add
            Variables to add to kwargs

        Returns
        -------
        self
        """
        self._kwargs = dict(self._kwargs, **variables_to_add)
        return self

    def get_download_info_json_name(self) -> str:
        """
        Returns
        -------
        The download info json's file name
        """
        return f"{self.uid}.{self.info_json_ext}"

    def get_download_info_json_path(self) -> str:
        """
        Returns
        -------
        Entry's downloaded info json file path
        """
        return str(Path(self.working_directory()) / self.get_download_info_json_name())

    @final
    def to_type(self, entry_type: Type[TBaseEntry]) -> TBaseEntry:
        """
        Returns
        -------
        Converted EntryParent to Entry-like class
        """
        return entry_type(entry_dict=self._kwargs, working_directory=self._working_directory)

    @classmethod
    def is_entry_parent(cls, entry_dict: Dict | TBaseEntry):
        """
        Returns
        -------
        True if it is a parent. False otherwise
        """
        entry_type: Optional[str] = None
        if isinstance(entry_dict, cls):
            entry_type = entry_dict._kwargs_get("_type")
        if isinstance(entry_dict, dict):
            entry_type = entry_dict.get("_type")

        return entry_type == "playlist"

    @classmethod
    def is_entry(cls, entry_dict: Dict | TBaseEntry):
        """
        Returns
        -------
        True if it is an entry. False otherwise
        """
        entry_ext: Optional[str] = None
        if isinstance(entry_dict, cls):
            entry_ext = entry_dict._kwargs_get("ext")
        if isinstance(entry_dict, dict):
            entry_ext = entry_dict.get("ext")

        return entry_ext is not None

    def ytdl_uid(self) -> str:
        """
        Returns
        -------
        extractor + uid, making this a unique hash for any entry
        """
        return self.download_archive_extractor + self.uid
