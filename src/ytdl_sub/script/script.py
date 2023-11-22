from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.script.parser import parse
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import CycleDetected


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

    def _traverse_custom_function_dependencies(
        self,
        custom_function_name: str,
        custom_function_dependency: SyntaxTree,
        deps: List[str],
    ) -> None:
        for dep in custom_function_dependency.custom_functions:
            if custom_function_name in deps + [dep.name]:
                cycle_deps = [custom_function_name] + deps + [dep.name]
                cycle_deps_str = " -> ".join([f"%{name}" for name in cycle_deps])
                raise CycleDetected(f"Custom functions contain a cycle: {cycle_deps_str}")

            self._traverse_custom_function_dependencies(
                custom_function_name=custom_function_name,
                custom_function_dependency=self._functions[dep.name],
                deps=deps + [dep.name],
            )

    def _ensure_no_custom_function_cycles(self):
        for custom_function_name, custom_function in self._functions.items():
            self._traverse_custom_function_dependencies(
                custom_function_name=custom_function_name,
                custom_function_dependency=custom_function,
                deps=[],
            )

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

        self._ensure_no_custom_function_cycles()

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
        overrides: Dict[Variable, SyntaxTree] = {
            Variable(name): ast for name, ast in self._variables.items()
        }

        unresolved_variables: List[Variable] = list(overrides.keys())
        resolved_variables: Dict[Variable, Resolvable] = (
            pre_resolved_variables if pre_resolved_variables else {}
        )

        while unresolved_variables:
            unresolved_count: int = len(unresolved_variables)

            for variable in unresolved_variables:
                if not overrides[variable].has_variable_dependency(
                    resolved_variables=resolved_variables
                ):
                    resolved_variables[variable] = overrides[variable].resolve(
                        resolved_variables=resolved_variables,
                        custom_functions=self._functions,
                    )
                    unresolved_variables.remove(variable)

            if len(unresolved_variables) == unresolved_count:
                raise CycleDetected(
                    f"Cycle detected within these variables: "
                    f"{', '.join(sorted([var.name for var in unresolved_variables]))}"
                )

        return {variable.name: resolvable for variable, resolvable in resolved_variables.items()}
