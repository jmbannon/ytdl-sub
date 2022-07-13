from abc import ABC
from typing import Any
from typing import Dict


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

        self._additional_variables: Dict[str, str] = {}

    def kwargs_contains(self, key: str) -> bool:
        """Returns whether internal kwargs contains the specified key"""
        return key in self._kwargs

    def kwargs(self, key) -> Any:
        """Returns an internal kwarg value supplied from ytdl"""
        if not self.kwargs_contains(key):
            raise KeyError(f"Expected '{key}' in {self.__class__.__name__} but does not exist.")
        return self._kwargs[key]

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
