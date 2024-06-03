# pylint: disable=missing-raises-doc
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.script.functions import Functions
from ytdl_sub.script.parser import parse
from ytdl_sub.script.script_output import ScriptOutput
from ytdl_sub.script.types.resolvable import BuiltInFunctionType
from ytdl_sub.script.types.resolvable import Lambda
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import UNREACHABLE
from ytdl_sub.script.utils.exceptions import CycleDetected
from ytdl_sub.script.utils.exceptions import IncompatibleFunctionArguments
from ytdl_sub.script.utils.exceptions import InvalidCustomFunctionArguments
from ytdl_sub.script.utils.exceptions import RuntimeException
from ytdl_sub.script.utils.exceptions import ScriptVariableNotResolved
from ytdl_sub.script.utils.name_validation import validate_variable_name
from ytdl_sub.script.utils.type_checking import FunctionSpec


def _is_function(override_name: str):
    return override_name.startswith("%")


def _function_name(function_key: str) -> str:
    """
    Drop the % in %custom_function
    """
    return function_key[1:]


def _to_function_definition_name(function_key: str) -> str:
    """
    Add % in %custom_function
    """
    return f"%{function_key}"


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

    def _ensure_no_variable_cycles(self, variables: Dict[str, SyntaxTree]):
        for variable_name, variable_definition in variables.items():
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
        self, prefix: str, name: str, definition: SyntaxTree
    ):
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

    def _get_lambda_function_names_to_evaluate(self, function: BuiltInFunctionType) -> Set[str]:
        lambda_function_names: Set[str] = set()
        for lamb in SyntaxTree(function.args).lambdas:
            if lamb in function.args:
                lambda_function_names.add(lamb.value)

            # See if the arg outputs a lambda (from an if).
            # If so, add the possible lambda to be checked
            for arg in function.args:
                if (
                    isinstance(arg, BuiltInFunctionType)
                    and arg.output_type() == Lambda
                    and lamb in arg.args
                ):
                    lambda_function_names.add(lamb.value)

        return lambda_function_names

    def _ensure_lambda_usage_num_input_arguments_valid(
        self, prefix: str, name: str, definition: SyntaxTree
    ):
        for function in definition.built_in_functions:
            for arg in function.args:
                self._ensure_lambda_usage_num_input_arguments_valid(
                    prefix=prefix, name=name, definition=SyntaxTree([arg])
                )

            spec = FunctionSpec.from_callable(
                name=function.name, callable_ref=Functions.get(function.name)
            )
            if not (lambda_type := spec.is_lambda_like):
                return

            lambda_function_names = self._get_lambda_function_names_to_evaluate(function=function)

            # Only case len(lambda_function_names) > 1 is when used in if-statements
            for lambda_function_name in lambda_function_names:
                if Functions.is_built_in(lambda_function_name):
                    lambda_spec = FunctionSpec.from_callable(
                        name=lambda_function_name, callable_ref=Functions.get(lambda_function_name)
                    )
                    if not lambda_spec.is_num_args_compatible(lambda_type.num_input_args()):
                        expected_args_str = str(lambda_spec.num_required_args)
                        if lambda_spec.num_required_args != len(lambda_spec.args):
                            expected_args_str = f"{expected_args_str} - {len(lambda_spec.args)}"

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

    def _validate(self, added_variables: Optional[Set[str]] = None) -> None:
        variables = self._variables
        if added_variables is not None:
            variables = {
                name: ast for name, ast in self._variables.items() if name in added_variables
            }

        if added_variables is None:
            self._ensure_no_custom_function_cycles()
            self._ensure_custom_function_arguments_valid()

        self._ensure_no_variable_cycles(variables)

        to_validate = [("Variable ", variables)]
        if added_variables is None:
            to_validate.append(("Custom function %", self._functions))

        for prefix, definitions in to_validate:
            for name, definition in definitions.items():
                self._ensure_custom_function_usage_num_input_arguments_valid(
                    prefix=prefix, name=name, definition=definition
                )
                self._ensure_lambda_usage_num_input_arguments_valid(
                    prefix=prefix, name=name, definition=definition
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

    def _recursive_get_unresolved_output_filter_variables(
        self, current_var: SyntaxTree, subset_to_resolve: Set[str], unresolvable: Set[Variable]
    ) -> Set[str]:
        for var_dep in current_var.variables:
            if var_dep in unresolvable:
                raise ScriptVariableNotResolved(
                    f"Output filter variable contains the variable {var_dep} "
                    f"which is set as unresolvable"
                )

            # Do not recurse custom function arguments since they have no deps
            if isinstance(var_dep, FunctionArgument):
                continue

            subset_to_resolve.add(var_dep.name)
            subset_to_resolve |= self._recursive_get_unresolved_output_filter_variables(
                current_var=self._variables[var_dep.name],
                subset_to_resolve=subset_to_resolve,
                unresolvable=unresolvable,
            )
        for custom_func_dep in current_var.custom_functions:
            subset_to_resolve |= self._recursive_get_unresolved_output_filter_variables(
                current_var=self._functions[custom_func_dep.name],
                subset_to_resolve=subset_to_resolve,
                unresolvable=unresolvable,
            )

        return subset_to_resolve

    def _get_unresolved_output_filter(
        self,
        unresolved: Dict[Variable, SyntaxTree],
        output_filter: Set[str],
        unresolvable: Set[Variable],
    ) -> Dict[Variable, SyntaxTree]:
        """
        When an output filter is applied, only a subset of variables that the filter
        depends on need to be resolved.
        """
        subset_to_resolve: Set[str] = set()

        for output_filter_variable in output_filter:
            subset_to_resolve.add(output_filter_variable)

            if output_filter_variable not in self._variables:
                raise ScriptVariableNotResolved(
                    "Tried to specify an output filter variable that does not exist"
                )

            subset_to_resolve |= self._recursive_get_unresolved_output_filter_variables(
                current_var=self._variables[output_filter_variable],
                subset_to_resolve=subset_to_resolve,
                unresolvable=unresolvable,
            )

        return {var: syntax for var, syntax in unresolved.items() if var.name in subset_to_resolve}

    def _resolve(
        self,
        pre_resolved: Optional[Dict[str, Resolvable]] = None,
        unresolvable: Optional[Set[str]] = None,
        update: bool = False,
        output_filter: Optional[Set[str]] = None,
    ) -> ScriptOutput:
        """
        Parameters
        ----------
        pre_resolved
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

        Raises
        ------
        ScriptVariableNotResolved
            If specifying a filter of variable to resolve, and one of them does not.
        """
        resolved: Dict[Variable, Resolvable] = {
            Variable(name): value for name, value in (pre_resolved or {}).items()
        }

        unresolvable: Set[Variable] = {Variable(name) for name in (unresolvable or {})}
        unresolved_filter = set(resolved.keys()).union(unresolvable)
        unresolved: Dict[Variable, SyntaxTree] = {
            Variable(name): ast
            for name, ast in self._variables.items()
            if Variable(name) not in unresolved_filter
        }

        if output_filter:
            unresolved = self._get_unresolved_output_filter(
                unresolved=unresolved,
                output_filter=output_filter,
                unresolvable=unresolvable,
            )

        while unresolved:
            unresolved_count: int = len(unresolved)

            for variable in list(unresolved.keys()):
                definition = unresolved[variable]

                # If the definition is already a resolvable, mark it as such
                if resolvable := definition.maybe_resolvable:
                    resolved[variable] = resolvable
                    del unresolved[variable]

                # If the variable's variable dependencies contain an unresolvable variable,
                # declare it as unresolvable and continue
                elif definition.contains(unresolvable, custom_function_definitions=self._functions):
                    unresolvable.add(variable)
                    del unresolved[variable]

                # Otherwise, if it has dependencies that are all resolved, then
                # resolve the definition
                elif not definition.is_subset_of(
                    variables=resolved.keys(), custom_function_definitions=self._functions
                ):
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

        if output_filter:
            for name in output_filter:
                if name not in resolved_variables:
                    raise ScriptVariableNotResolved(f"Specified {name} to resolve, but it did not")

            return ScriptOutput(
                {
                    name: resolvable
                    for name, resolvable in resolved_variables.items()
                    if name in output_filter
                }
            )

        return ScriptOutput(resolved_variables)

    def resolve(
        self,
        resolved: Optional[Dict[str, Resolvable]] = None,
        unresolvable: Optional[Set[str]] = None,
        update: bool = False,
    ) -> ScriptOutput:
        """
        Resolves the script

        Parameters
        ----------
        resolved
            Optional. Pre-resolved variables that should be used instead of what is in the script.
        unresolvable
            Optional. Unresolvable variables that will be ignored in resolution, including all
            variables with a dependency to them.
        update
            Whether to update the script's internal values with the resolved variables instead of
            their original definition. This helps avoid re-evaluated the same variables repeatedly.

        Returns
        -------
        ScriptOutput
            Containing all resolved variables.
        """
        return self._resolve(
            pre_resolved=resolved, unresolvable=unresolvable, update=update, output_filter=None
        )

    def add(self, variables: Dict[str, str], unresolvable: Optional[Set[str]] = None) -> "Script":
        """
        Adds parses and adds new variables to the script.

        Parameters
        ----------
        variables
            Mapping containing variable name to definition.
        unresolvable
            Optional. Set of unresolved variables that the new variables may contain, but the
            script does not (yet).

        Returns
        -------
        Script
            self
        """
        added_variables_to_validate: Set[str] = set()

        functions_to_add = {
            _function_name(name): definition
            for name, definition in variables.items()
            if _is_function(name)
        }
        variables_to_add = {
            name: definition for name, definition in variables.items() if not _is_function(name)
        }

        for definitions in [functions_to_add, variables_to_add]:
            for name, definition in definitions.items():
                parsed = parse(
                    text=definition,
                    name=name,
                    custom_function_names=set(self._functions.keys()),
                    variable_names=set(self._variables.keys())
                    .union(variables.keys())
                    .union(unresolvable or set()),
                )

                if parsed.maybe_resolvable is None:
                    added_variables_to_validate.add(name)

                if name in functions_to_add:
                    self._functions[name] = parsed
                else:
                    self._variables[name] = parsed

        if added_variables_to_validate:
            self._validate(added_variables=added_variables_to_validate)

        return self

    def resolve_once(
        self,
        variable_definitions: Dict[str, str],
        resolved: Optional[Dict[str, Resolvable]] = None,
        unresolvable: Optional[Set[str]] = None,
    ) -> Dict[str, Resolvable]:
        """
        Given a new set of variable definitions, resolve them using the Script, but do not
        add them to the Script itself.

        Parameters
        ----------
        variable_definitions
            Variables to resolve, but not store in the Script
        resolved
            Optional. Pre-resolved variables that should be used instead of what is in the script.
        unresolvable
            Optional. Unresolvable variables that will be ignored in resolution, including all
            variables with a dependency to them.

        Returns
        -------
        Dict[str, Resolvable]
            Dict containing the variable names to their resolved values.
        """
        try:
            self.add(variable_definitions)
            return self._resolve(
                pre_resolved=resolved,
                unresolvable=unresolvable,
                output_filter=set(list(variable_definitions.keys())),
            ).output
        finally:
            for name in variable_definitions.keys():
                if name in self._variables:
                    del self._variables[name]

    def get(self, variable_name: str) -> Resolvable:
        """
        Parameters
        ----------
        variable_name
            Name of the resolved variable to get.

        Returns
        -------
        Resolvable
            The resolved variable of the given name.

        Raises
        ------
        RuntimeException
            If the variable has not been resolved yet in the Script.
        """
        if variable_name not in self._variables:
            raise RuntimeException(
                f"Tried to get resolved variable {variable_name}, but it does not exist"
            )

        if (resolvable := self._variables[variable_name].maybe_resolvable) is not None:
            return resolvable

        raise RuntimeException(f"Tried to get unresolved variable {variable_name}")

    @property
    def variable_names(self) -> Set[str]:
        """
        Returns
        -------
        Set[str]
            Names of all the variables within the Script.
        """
        return set(list(self._variables.keys()))

    @property
    def function_names(self) -> Set[str]:
        """
        Returns
        -------
        Set[str]
            Names of all functions within the Script.
        """
        return set(_to_function_definition_name(name) for name in self._functions.keys())
