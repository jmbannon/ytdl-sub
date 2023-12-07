import copy
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.script.functions import Functions
from ytdl_sub.script.parser import parse
from ytdl_sub.script.script_output import ScriptOutput
from ytdl_sub.script.types.resolvable import Lambda
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import UNREACHABLE
from ytdl_sub.script.utils.exceptions import CycleDetected
from ytdl_sub.script.utils.exceptions import FunctionDoesNotExist
from ytdl_sub.script.utils.exceptions import IncompatibleFunctionArguments
from ytdl_sub.script.utils.exceptions import InvalidCustomFunctionArguments
from ytdl_sub.script.utils.exceptions import RuntimeException
from ytdl_sub.script.utils.exceptions import ScriptBuilderMissingDefinitions
from ytdl_sub.script.utils.exceptions import VariableDoesNotExist
from ytdl_sub.script.utils.name_validation import validate_variable_name
from ytdl_sub.script.utils.type_checking import FunctionSpec

# pylint: disable=missing-raises-doc


def _is_function(override_name: str):
    return override_name.startswith("%")


def _function_name(function_key: str) -> str:
    """
    Drop the % in %custom_function
    """
    return function_key[1:]


class Script:
    """
    Takes a dictionary of both
        ``{ variable_names: syntax }``
    and
        ``{ %custom_function: syntax }``
    """

    def _ensure_no_cycle(
        self, name: str, dep: str, deps: List[str], definitions: Dict[str, SyntaxTree]
    ):
        if dep not in definitions:
            return  # does not exist, will throw downstream in parser

        if name in deps + [dep]:
            type_name, pre = (
                ("custom functions", "%") if definitions is self._functions else ("variables", "")
            )
            cycle_deps = [name] + deps + [dep]
            cycle_deps_str = " -> ".join([f"{pre}{name}" for name in cycle_deps])

            raise CycleDetected(f"Cycle detected within these {type_name}: {cycle_deps_str}")

    def _traverse_variable_dependencies(
        self,
        variable_name: str,
        variable_dependency: SyntaxTree,
        deps: List[str],
    ) -> None:
        for dep in variable_dependency.variables:
            self._ensure_no_cycle(
                name=variable_name, dep=dep.name, deps=deps, definitions=self._variables
            )
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
            self._ensure_no_cycle(
                name=custom_function_name, dep=dep.name, deps=deps, definitions=self._functions
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

    def _ensure_custom_function_usage_num_input_arguments_valid(
        self, definitions: Dict[str, SyntaxTree], prefix: str
    ):
        for name, definition in definitions.items():
            for nested_custom_function in definition.custom_functions:
                if nested_custom_function.num_input_args != (
                    expected_num_args := len(
                        self._functions[nested_custom_function.name].function_arguments
                    )
                ):
                    raise InvalidCustomFunctionArguments(
                        f"{prefix}{name} has invalid usage of the custom "
                        f"function %{nested_custom_function.name}: Expects {expected_num_args} "
                        f"argument{'s' if expected_num_args > 1 else ''} but received "
                        f"{nested_custom_function.num_input_args}"
                    )

    def _ensure_lambda_usage_num_input_arguments_valid(
        self, definitions: Dict[str, SyntaxTree], prefix: str
    ):
        for name, definition in definitions.items():
            for function in definition.built_in_functions:
                spec = FunctionSpec.from_callable(Functions.get(function.name))
                if lambda_type := spec.is_lambda_function:

                    lambda_function_names = set(
                        [
                            lamb.value
                            for lamb in SyntaxTree(function.args).lambdas
                            if isinstance(lamb, Lambda)
                        ]
                    )

                    # Only case len(lambda_function_names) > 1 is when used in if-statements
                    for lambda_function_name in lambda_function_names:
                        if Functions.is_built_in(lambda_function_name):
                            lambda_spec = FunctionSpec.from_callable(
                                Functions.get(lambda_function_name)
                            )
                            if not lambda_spec.is_num_args_compatible(lambda_type.num_input_args()):
                                expected_args_str = str(lambda_spec.num_required_args)
                                if lambda_spec.num_required_args != len(lambda_spec.args):
                                    expected_args_str = (
                                        f"{expected_args_str} - {len(lambda_spec.args)}"
                                    )

                                raise IncompatibleFunctionArguments(
                                    f"{prefix}{name} has invalid usage of the "
                                    f"function %{lambda_function_name} as a lambda: "
                                    f"Expects {expected_args_str} "
                                    f"argument{'s' if expected_args_str != '1' else ''} but will "
                                    f"receive {lambda_type.num_input_args()}."
                                )
                        else:  # is custom function
                            if lambda_function_name not in self._functions:
                                raise UNREACHABLE  # Custom function should have been validated

                            expected_num_arguments = len(
                                self._functions[lambda_function_name].function_arguments
                            )
                            if lambda_type.num_input_args() != expected_num_arguments:
                                raise IncompatibleFunctionArguments(
                                    f"{prefix}{name} has invalid usage of the custom "
                                    f"function %{lambda_function_name} as a lambda: "
                                    f"Expects {expected_num_arguments} "
                                    f"argument{'s' if expected_num_arguments > 1 else ''} but will "
                                    f"receive {lambda_type.num_input_args()}."
                                )

    def _validate(self) -> None:
        self._ensure_no_custom_function_cycles()
        self._ensure_custom_function_arguments_valid()
        self._ensure_no_variable_cycles()

        for prefix, definitions in (
            ("Variable ", self._variables),
            ("Custom function %", self._functions),
        ):
            self._ensure_custom_function_usage_num_input_arguments_valid(
                prefix=prefix, definitions=definitions
            )
            self._ensure_lambda_usage_num_input_arguments_valid(
                prefix=prefix, definitions=definitions
            )

    def __init__(self, script: Dict[str, str]):
        function_names: Set[str] = {
            _function_name(name) for name in script.keys() if _is_function(name)
        }
        variable_names: Set[str] = {
            validate_variable_name(name) for name in script.keys() if not _is_function(name)
        }

        self._functions: Dict[str, SyntaxTree] = {
            # custom_function_name must be passed to properly type custom function
            # arguments uniquely if they're nested (i.e. $0 to $custom_func___0)
            _function_name(function_key): parse(
                text=function_value,
                name=_function_name(function_key),
                custom_function_names=function_names,
                variable_names=variable_names,
            )
            for function_key, function_value in script.items()
            if _is_function(function_key)
        }

        self._variables: Dict[str, SyntaxTree] = {
            variable_key: parse(
                text=variable_value,
                name=variable_key,
                custom_function_names=function_names,
                variable_names=variable_names,
            )
            for variable_key, variable_value in script.items()
            if not _is_function(variable_key)
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
    ) -> ScriptOutput:
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

        return ScriptOutput(resolved_variables)

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


class ScriptBuilder:
    """
    Takes a dictionary of both
        ``{ variable_names: syntax }``
    and
        ``{ %custom_function: syntax }``
    """

    def __init__(self, script: Dict[str, str]):
        self._functions: Dict[str, SyntaxTree] = {
            # custom_function_name must be passed to properly type custom function
            # arguments uniquely if they're nested (i.e. $0 to $custom_func___0)
            _function_name(function_key): parse(
                text=function_value,
                name=_function_name(function_key),
            )
            for function_key, function_value in script.items()
            if _is_function(function_key)
        }

        self._variables: Dict[str, SyntaxTree] = {
            variable_key: parse(
                text=variable_value,
                name=variable_key,
            )
            for variable_key, variable_value in script.items()
            if not _is_function(variable_key)
        }

    def add(self, variables: Dict[str, str]) -> "ScriptBuilder":
        for variable_name, variable_definition in variables.items():
            self._variables[variable_name] = parse(
                text=variable_definition,
                name=variable_name,
            )
        return self

    @property
    def _missing_metadata(self) -> Dict[str, Set[str]]:
        missing_metadata: Dict[str, Set[str]] = {}

        defined_variables: Set[str] = set(self._variables.keys())
        defined_functions: Set[str] = set(self._functions.keys())
        for name, variable in self._variables.items():
            missing_metadata[name] = {var.name for var in variable.variables}.difference(
                defined_variables
            )
            missing_metadata[name].update(
                {fun.name for fun in variable.custom_functions}.difference(defined_functions)
            )

        for name, function in self._functions.items():
            missing_metadata[name] = {var.name for var in function.variables}.difference(
                defined_variables
            )
            missing_metadata[name].update(
                {fun.name for fun in function.custom_functions}.difference(defined_functions)
            )

        return missing_metadata

    @classmethod
    def _build(cls, variables: Dict[str, SyntaxTree], functions: Dict[str, SyntaxTree]) -> Script:
        script = Script({})
        script._variables = variables
        script._functions = functions
        script._validate()
        return script

    def partial_build(self) -> Script:
        missing_metadata = self._missing_metadata
        maybe_resolvable_variables: Dict[str, SyntaxTree] = {
            name: variable
            for name, variable in self._variables.items()
            if name not in missing_metadata
        }
        maybe_resolvable_functions: Dict[str, SyntaxTree] = {
            name: function
            for name, function in self._functions.items()
            if name not in missing_metadata
        }

        return self._build(
            variables=maybe_resolvable_variables, functions=maybe_resolvable_functions
        )

    def build(self) -> Script:
        for name, missing_metadata in self._missing_metadata.items():
            if missing_metadata:
                raise ScriptBuilderMissingDefinitions(
                    f"{name} is missing the following definitions: {', '.join(missing_metadata)}"
                )

        return self._build(variables=self._variables, functions=self._functions)
