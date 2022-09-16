from abc import ABC
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import final

from yt_dlp.utils import sanitize_filename

# pylint: disable=no-member


class BaseEntryVariables:
    """
    Source variables are ``{variables}`` that contain metadata from downloaded media.
    These variables can be used with fields that expect
    :class:`~ytdl_sub.validators.string_formatter_validators.StringFormatterValidator`,
    but not
    :class:`~ytdl_sub.validators.string_formatter_validators.OverridesStringFormatterValidator`.
    """

    @property
    def uid(self: "BaseEntry") -> str:
        """
        Returns
        -------
        str
            The entry's unique ID
        """
        return self.kwargs("id")

    @property
    def extractor(self: "BaseEntry") -> str:
        """
        Returns
        -------
        str
            The ytdl extractor name
        """
        return self.kwargs("extractor")

    @property
    def title(self: "BaseEntry") -> str:
        """
        Returns
        -------
        str
            The title of the entry. If a title does not exist, returns its unique ID.
        """
        return self.kwargs_get("title", self.uid)

    @property
    def title_sanitized(self) -> str:
        """
        Returns
        -------
        str
            The sanitized title of the entry, which is safe to use for Unix and Windows file names.
        """
        return sanitize_filename(self.title)

    @property
    def webpage_url(self: "BaseEntry") -> str:
        """
        Returns
        -------
        str
            The url to the webpage.
        """
        return self.kwargs("webpage_url")

    @property
    def info_json_ext(self) -> str:
        """
        Returns
        -------
        str
            The "info.json" extension
        """
        return "info.json"

    def base_variable_dict(self) -> Dict[str, str]:
        """
        Returns
        -------
        BaseEntry variables that can be nested for playlist, source, etc
        """
        return {
            "uid": self.uid,
            "extractor": self.extractor,
            "title": self.title,
            "title_sanitized": self.title_sanitized,
            "webpage_url": self.webpage_url,
        }


# pylint: enable=no-member


TBaseEntry = TypeVar("TBaseEntry", bound="BaseEntry")


class BaseEntry(BaseEntryVariables, ABC):
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

        self._additional_variables: Dict[str, str | int] = {}

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

    def add_variables(self, variables_to_add: Dict[str, str]) -> "BaseEntry":
        """
        Parameters
        ----------
        variables_to_add
            Variables to add to this entry

        Returns
        -------
        self

        Raises
        ------
        ValueError
            If a variable trying to be added already exists as a source variable
        """
        for variable_name in variables_to_add.keys():
            if self.kwargs_contains(variable_name):
                raise ValueError(
                    f"Cannot add variable '{variable_name}': already exists in the kwargs"
                )

        self._additional_variables = dict(self._additional_variables, **variables_to_add)
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

    def _added_variables(self) -> Dict[str, str]:
        """
        Returns
        -------
        Dict of variables added to this entry
        """
        return self._additional_variables

    @classmethod
    def source_variables(cls) -> List[str]:
        """
        Returns
        -------
        List of all source variables
        """
        property_names = [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property)]
        return property_names

    @final
    def to_dict(self) -> Dict[str, str]:
        """
        Returns
        -------
        Dictionary containing all variables
        """
        source_variable_dict = {
            source_var: getattr(self, source_var) for source_var in self.source_variables()
        }
        return dict(source_variable_dict, **self._added_variables())

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
