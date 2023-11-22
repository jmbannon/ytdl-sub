from typing import Dict
from typing import Optional

from ytdl_sub.script.parser import parse
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import Variable


class Script:
    """
    Takes a dictionary of both
        ``{ variable_names: syntax }``
    and
        ``{ %custom_function: syntax }``
    """

    @classmethod
    def _is_function(cls, override_name: str):
        return override_name.startswith("%")

    @classmethod
    def _function_name(cls, function_key: str) -> str:
        """
        Drop the % in %custom_function
        """
        return function_key[1:]

    def __init__(self, overrides: Dict[str, str]):
        self._functions: Dict[str, SyntaxTree] = {
            # custom_function_name must be passed to properly type custom function
            # arguments uniquely if they're nested (i.e. $0 to $custom_func___0)
            self._function_name(function_key): parse(
                text=function_value, custom_function_name=self._function_name(function_key)
            )
            for function_key, function_value in overrides.items()
            if self._is_function(function_key)
        }

        self._variables: Dict[str, SyntaxTree] = {
            override_name: parse(override_value)
            for override_name, override_value in overrides.items()
            if not self._is_function(override_name)
        }

    def resolve(
        self, pre_resolved_variables: Optional[Dict[Variable, Resolvable]] = None
    ) -> Dict[str, Resolvable]:
        """
        Parameters
        ----------
        pre_resolved_variables
            Optional variables that have been resolved elsewhere and could be used in this script

        Returns
        -------
        Dict of resolved values
        """
        return SyntaxTree.resolve_overrides(
            parsed_overrides=self._variables,
            custom_functions=self._functions,
            pre_resolved_variables=pre_resolved_variables,
        )
