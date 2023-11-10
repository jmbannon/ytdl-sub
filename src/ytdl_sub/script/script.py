from typing import Dict, Optional

from ytdl_sub.script.parser import parse
from ytdl_sub.script.syntax_tree import SyntaxTree
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.variable import Variable


class Script:
    @classmethod
    def _is_function(cls, override_name: str):
        return override_name.startswith("%")

    @classmethod
    def _function_name(self, function_key: str) -> str:
        return function_key[1:]

    def __init__(self, overrides: Dict[str, str]):
        self._functions: Dict[str, SyntaxTree] = {
            self._function_name(function_key): parse(function_value)
            for function_key, function_value in overrides.items()
            if self._is_function(function_key)
        }

        self._variables: Dict[str, SyntaxTree] = {
            override_name: parse(override_value)
            for override_name, override_value in overrides.items()
            if not self._is_function(override_name)
        }

    def resolve(self, pre_resolved_variables: Optional[Dict[Variable, Resolvable]] = None) -> Dict[str, Resolvable]:
        return SyntaxTree.resolve_overrides(
            parsed_overrides=self._variables,
            custom_functions=self._functions,
            pre_resolved_variables=pre_resolved_variables,
        )