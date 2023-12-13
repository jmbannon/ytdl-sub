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
    def uid(self: "BaseEntry") -> str:
        """
        Returns
        -------
        str
            The entry's unique ID
        """
        return str(self.kwargs(v.uid.metadata_key))

    @property
    def extractor(self: "BaseEntry") -> str:
        """
        The ytdl extractor name
        """
        # pylint: disable=line-too-long
        # Taken from https://github.com/yt-dlp/yt-dlp/blob/e6ab678e36c40ded0aae305bbb866cdab554d417/yt_dlp/YoutubeDL.py#L3514
        # pylint: enable=line-too-long
        return self.kwargs_get(v.extractor_key.metadata_key) or self.kwargs(v.ie_key.metadata_key)

    @property
    def title(self: "BaseEntry") -> str:
        """
        The title of the entry. If a title does not exist, returns its unique ID.
        """
        return self.kwargs_get(v.title.metadata_key, self.uid)

    @property
    def webpage_url(self: "BaseEntry") -> str:
        """
        The url to the webpage.
        """
        return self.kwargs(v.webpage_url.metadata_key)

    @property
    def info_json_ext(self) -> str:
        """The "info.json" extension"""
        return "info.json"

    @property
    def uploader_id(self: "BaseEntry") -> str:
        """
        The uploader id if it exists, otherwise return the unique ID.
        """
        return self.kwargs_get(v.uploader_id.metadata_key, self.uid)

    def kwargs_contains(self, key: str) -> bool:
        """Returns whether internal kwargs contains the specified key"""
        return key in self._kwargs

    def kwargs(self, key) -> Any:
        """Returns an internal kwarg value supplied from ytdl"""
        if not self.kwargs_contains(key):
            raise KeyError(f"Expected '{key}' in {self.__class__.__name__} but does not exist.")
        output = self._kwargs[key]

        # Replace curly braces with unicode version to avoid variable shenanigans
        if isinstance(output, str):
            return output.replace("{", "｛").replace("}", "｝")
        return output

    def kwargs_get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Dict get on kwargs
        """
        if not self.kwargs_contains(key) or self.kwargs(key) is None:
            return default
        return self.kwargs(key)

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
            entry_type = entry_dict.kwargs_get("_type")
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
            entry_ext = entry_dict.kwargs_get("ext")
        if isinstance(entry_dict, dict):
            entry_ext = entry_dict.get("ext")

        return entry_ext is not None

    def ytdl_uid(self) -> str:
        """
        Returns
        -------
        extractor + uid, making this a unique hash for any entry
        """
        return self.extractor + self.uid
