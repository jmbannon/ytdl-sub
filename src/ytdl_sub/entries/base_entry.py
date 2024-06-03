# pylint: disable=protected-access
from abc import ABC
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import final

from yt_dlp.utils import LazyList
from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions

v: VariableDefinitions = VARIABLES

BaseEntryT = TypeVar("BaseEntryT", bound="BaseEntry")


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

        # Sometimes yt-dlp can return a LazyList which is not JSON serializable.
        # Cast it to a native list here. (https://github.com/jmbannon/ytdl-sub/issues/910)
        for key in self._kwargs.keys():
            if isinstance(self._kwargs[key], LazyList):
                self._kwargs[key] = list(self._kwargs[key])

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
    def uid_sanitized(self) -> str:
        """
        Sanitized version, used in filenames
        """
        return sanitize_filename(self.uid)

    def base_filename(self, ext: str):
        """
        The base filename of all yt-dlp downloaded entry files
        """
        return f"{self.uid_sanitized}.{ext}"

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

    def get_download_info_json_name(self) -> str:
        """
        Returns
        -------
        The download info json's file name
        """
        return self.base_filename(ext=self.info_json_ext)

    def get_download_info_json_path(self) -> str:
        """
        Returns
        -------
        Entry's downloaded info json file path
        """
        return str(Path(self.working_directory()) / self.get_download_info_json_name())

    @final
    def to_type(self, entry_type: Type[BaseEntryT]) -> BaseEntryT:
        """
        Returns
        -------
        Converted EntryParent to Entry-like class
        """
        return entry_type(entry_dict=self._kwargs, working_directory=self._working_directory)

    @classmethod
    def is_entry_parent(cls, entry_dict: Dict | BaseEntryT):
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
    def is_entry(cls, entry_dict: Dict | BaseEntryT):
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
