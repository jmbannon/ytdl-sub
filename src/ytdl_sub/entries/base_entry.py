from abc import ABC
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
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
            The title of the entry
        """
        return self.kwargs("title")

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


# pylint: enable=no-member


class BaseEntry(BaseEntryVariables, ABC):
    """
    Abstract entry object to represent anything download from ytdl (playlist metadata, media, etc).
    """

    # The ytdl extractor type that the entry represents
    entry_extractor: str

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
