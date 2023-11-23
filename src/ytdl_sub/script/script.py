import copy
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.script.parser import parse
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import UNREACHABLE
from ytdl_sub.script.utils.exceptions import CycleDetected
from ytdl_sub.script.utils.exceptions import InvalidCustomFunctionArguments
from ytdl_sub.script.utils.exceptions import RuntimeException
from ytdl_sub.script.utils.name_validation import validate_variable_name

# pylint: disable=missing-raises-doc


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

    def _traverse_variable_dependencies(
        self,
        variable_name: str,
        variable_dependency: SyntaxTree,
        deps: List[str],
    ) -> None:
        for dep in variable_dependency.variables:
            if dep.name not in self._variables:
                continue  # does not exist, will throw downstream in parser

            if variable_name in deps + [dep.name]:
                cycle_deps = [variable_name] + deps + [dep.name]
                cycle_deps_str = " -> ".join(cycle_deps)
                raise CycleDetected(f"Cycle detected within these variables: {cycle_deps_str}")

            self._traverse_variable_dependencies(
                variable_name=variable_name,
                variable_dependency=self._variables[dep.name],
                deps=deps + [dep.name],
            )

    def _ensure_no_variable_cycles(self):
        for variable_name, variable_definition in self._variables.items():
            self._traverse_variable_dependencies(
                variable_name=variable_name,
                variable_dependency=variable_definition,
                deps=[],
            )

    def _traverse_custom_function_dependencies(
        self,
        custom_function_name: str,
        custom_function_dependency: SyntaxTree,
        deps: List[str],
    ) -> None:
        for dep in custom_function_dependency.custom_functions:
            if dep.name not in self._functions:
                continue  # does not exist, will throw downstream in parser

            if custom_function_name in deps + [dep.name]:
                cycle_deps = [custom_function_name] + deps + [dep.name]
                cycle_deps_str = " -> ".join([f"%{name}" for name in cycle_deps])
                raise CycleDetected(
                    f"Cycle detected within these custom functions: {cycle_deps_str}"
                )

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

    def _ensure_custom_function_arguments_valid(self):
        for custom_function_name, custom_function in self._functions.items():
            indices = sorted([arg.index for arg in custom_function.function_arguments])
            if indices != list(range(len(indices))):
                if len(indices) == 1:
                    raise InvalidCustomFunctionArguments(
                        f"Custom function %{custom_function_name} has invalid function arguments: "
                        f"The argument must start with $0, not ${indices[0]}."
                    )
                raise InvalidCustomFunctionArguments(
                    f"Custom function %{custom_function_name} has invalid function arguments: "
                    f"{', '.join(sorted(f'${idx}' for idx in indices))} "
                    f"do not increment from $0 to ${len(indices) - 1}."
                )

    def _ensure_custom_function_usage_num_input_arguments_valid(self):
        for variable_name, variable_definition in self._variables.items():
            for nested_custom_function in variable_definition.custom_functions:
                if nested_custom_function.num_input_args != (
                    expected_num_args := len(
                        self._functions[nested_custom_function.name].function_arguments
                    )
                ):
                    raise InvalidCustomFunctionArguments(
                        f"Variable {variable_name} has invalid usage of the custom "
                        f"function %{nested_custom_function.name}: Expects {expected_num_args} "
                        f"argument{'s' if expected_num_args > 1 else ''} but received "
                        f"{nested_custom_function.num_input_args}"
                    )

        for function_name, function_definition in self._functions.items():
            for nested_custom_function in function_definition.custom_functions:
                if nested_custom_function.name == function_name:
                    # Do not need to validate a cycle that should not exist
                    continue

                if nested_custom_function.num_input_args != (
                    expected_num_args := len(
                        self._functions[nested_custom_function.name].function_arguments
                    )
                ):
                    raise InvalidCustomFunctionArguments(
                        f"Custom function %{function_name} has invalid usage of the custom "
                        f"function %{nested_custom_function.name}: Expects {expected_num_args} "
                        f"argument{'s' if expected_num_args > 1 else ''} but received "
                        f"{nested_custom_function.num_input_args}"
                    )

    def _validate(self) -> None:
        self._ensure_no_custom_function_cycles()
        self._ensure_custom_function_arguments_valid()
        self._ensure_no_variable_cycles()
        self._ensure_custom_function_usage_num_input_arguments_valid()

    def __init__(self, script: Dict[str, str]):
        function_names: Set[str] = {
            self._function_name(name) for name in script.keys() if self._is_function(name)
        }
        variable_names: Set[str] = {
            validate_variable_name(name) for name in script.keys() if not self._is_function(name)
        }

        self._functions: Dict[str, SyntaxTree] = {
            # custom_function_name must be passed to properly type custom function
            # arguments uniquely if they're nested (i.e. $0 to $custom_func___0)
            self._function_name(function_key): parse(
                text=function_value,
                name=self._function_name(function_key),
                custom_function_names=function_names,
                variable_names=variable_names,
            )
            for function_key, function_value in script.items()
            if self._is_function(function_key)
        }

        self._variables: Dict[str, SyntaxTree] = {
            variable_key: parse(
                text=variable_value,
                name=variable_key,
                custom_function_names=function_names,
                variable_names=variable_names,
            )
            for variable_key, variable_value in script.items()
            if not self._is_function(variable_key)
        }
        self._validate()

    def _update_internally(self, resolved_variables: Dict[str, Resolvable]) -> None:
        for variable_name, resolved in resolved_variables.items():
            self._variables[variable_name] = SyntaxTree(ast=[resolved])

    def resolve(
        self,
        resolved: Optional[Dict[str, Resolvable]] = None,
        unresolvable: Optional[Set[str]] = None,
        update: bool = False,
    ) -> Dict[str, Resolvable]:
        """
        Parameters
        ----------
        resolved
            Optional. Variables that have been resolved elsewhere and could be used in this script
        unresolvable
            Optional. Variables that cannot be resolved, forcing any variable that depends on it
            to not be resolved.
        update
            Optional. Whether to update the internal representation of variables with their
            resolved value (if they get resolved).

        Returns
        -------
        Dict of resolved values
        """
        resolved: Dict[Variable, Resolvable] = {
            Variable(name): value for name, value in (resolved or {}).items()
        }
        unresolvable: Set[Variable] = {Variable(name) for name in (unresolvable or {})}
        unresolved: Dict[Variable, SyntaxTree] = {
            Variable(name): ast
            for name, ast in self._variables.items()
            if Variable(name) not in set(resolved.keys()).union(unresolvable)
        }

        while unresolved:
            unresolved_count: int = len(unresolved)

            for variable, definition in copy.deepcopy(unresolved).items():
                # If the variable's variable dependencies contain an unresolvable variable,
                # declare it as unresolvable and continue
                if definition.contains(unresolvable):
                    unresolvable.add(variable)
                    del unresolved[variable]

                # Otherwise, if it has dependencies that are all resolved, then
                # resolve the definition
                elif not definition.is_subset_of(variables=resolved.keys()):
                    resolved[variable] = unresolved[variable].resolve(
                        resolved_variables=resolved,
                        custom_functions=self._functions,
                    )
                    del unresolved[variable]

            if len(unresolved) == unresolved_count:
                # Implies a cycle within the variables. Should never reach
                # since cycles are detected in __init__
                raise UNREACHABLE

        resolved_variables = {
            variable.name: resolvable for variable, resolvable in resolved.items()
        }
        if update:
            self._update_internally(resolved_variables=resolved_variables)

        return resolved_variables

    def add(self, variables: Dict[str, str]) -> "Script":
        for variable_name, variable_definition in variables.items():
            self._variables[variable_name] = parse(
                text=variable_definition,
                name=variable_name,
                custom_function_names=set(self._functions.keys()),
                variable_names=set(self._variables.keys()).union(variables.keys()),
            )
        self._validate()
        return self

    def get(self, variable_name: str) -> Resolvable:
        if variable_name not in self._variables:
            raise RuntimeException(
                f"Tried to get resolved variable {variable_name}, but it does not exist"
            )

        if (resolvable := self._variables[variable_name].resolvable) is not None:
            return resolvable

        raise RuntimeException(f"Tried to get unresolved variable {variable_name}")
