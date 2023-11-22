import copy
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.script.types.resolvable import ArgumentType
from ytdl_sub.script.types.resolvable import NamedCustomFunction
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency
from ytdl_sub.script.utils.exceptions import CycleDetected
from ytdl_sub.utils.exceptions import StringFormattingException


@dataclass(frozen=True)
class SyntaxTree(VariableDependency):
    ast: List[ArgumentType]

    @property
    def _iterable_arguments(self) -> List[ArgumentType]:
        return self.ast

    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        resolved: List[Resolvable] = []
        for token in self.ast:
            resolved.append(
                self._resolve_argument_type(
                    arg=token,
                    resolved_variables=resolved_variables,
                    custom_functions=custom_functions,
                )
            )

        # If only one resolvable resides in the AST, return as that
        if len(resolved) == 1:
            return resolved[0]

        # Otherwise, to concat multiple resolved outputs, we must concat as strings
        return String("".join([str(res) for res in resolved]))

    @classmethod
    def _get_custom_function_dependencies(
        cls,
        custom_function_name: str,
        custom_function_dependency: "SyntaxTree",
        custom_functions: Dict[str, "SyntaxTree"],
        deps: List[str],
    ) -> List[str]:
        deps = copy.deepcopy(deps)  # do not work with references

        for dep in custom_function_dependency.custom_functions:
            # Skip leaf functions since they will never cause a cycle
            if not custom_functions[dep.name].custom_functions:
                continue

            deps.append(dep.name)

            if custom_function_name in deps:
                cycle_deps = [custom_function_name] + deps[0 : deps.index(custom_function_name) + 1]
                cycle_deps_str = " -> ".join([f"%{name}" for name in cycle_deps])
                raise CycleDetected(f"Custom functions contain a cycle: {cycle_deps_str}")

            deps += cls._get_custom_function_dependencies(
                custom_function_name=custom_function_name,
                custom_function_dependency=custom_functions[dep.name],
                custom_functions=custom_functions,
                deps=deps,
            )

        return deps

    @classmethod
    def _ensure_no_custom_function_cycles(cls, custom_functions: Dict[str, "SyntaxTree"]):
        for custom_function_name, custom_function in custom_functions.items():
            _ = cls._get_custom_function_dependencies(
                custom_function_name=custom_function_name,
                custom_function_dependency=custom_function,
                custom_functions=custom_functions,
                deps=[],
            )

    @classmethod
    def resolve_overrides(
        cls,
        parsed_overrides: Dict[str, "SyntaxTree"],
        custom_functions: Dict[str, "SyntaxTree"],
        pre_resolved_variables: Optional[Dict[Variable, Resolvable]],
    ) -> Dict[str, Resolvable]:
        overrides: Dict[Variable, "SyntaxTree"] = {
            Variable(name): ast for name, ast in parsed_overrides.items()
        }

        unresolved_variables: List[Variable] = list(overrides.keys())
        resolved_variables: Dict[Variable, Resolvable] = (
            pre_resolved_variables if pre_resolved_variables else {}
        )

        cls._ensure_no_custom_function_cycles(custom_functions=custom_functions)

        while unresolved_variables:
            unresolved_count: int = len(unresolved_variables)

            for variable in unresolved_variables:
                if not overrides[variable].has_variable_dependency(
                    resolved_variables=resolved_variables
                ):
                    resolved_variables[variable] = overrides[variable].resolve(
                        resolved_variables=resolved_variables,
                        custom_functions=custom_functions,
                    )
                    unresolved_variables.remove(variable)

            if len(unresolved_variables) == unresolved_count:
                raise StringFormattingException(
                    f"Cycle detected within these variables: "
                    f"{', '.join(sorted([var.name for var in unresolved_variables]))}"
                )

        return {variable.name: resolvable for variable, resolvable in resolved_variables.items()}
