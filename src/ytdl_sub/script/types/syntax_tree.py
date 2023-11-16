from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.script.types.resolvable import ArgumentType
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency
from ytdl_sub.utils.exceptions import StringFormattingException


@dataclass(frozen=True)
class SyntaxTree(VariableDependency):
    ast: List[ArgumentType]

    @property
    def variables(self) -> Set[Variable]:
        """
        Returns
        -------
        All variables used within the SyntaxTree
        """
        variables: Set[Variable] = set()
        for token in self.ast:
            if isinstance(token, Variable):
                variables.add(token)
            elif isinstance(token, VariableDependency):
                variables.update(token.variables)

        return variables

    @property
    def function_arguments(self) -> Set[FunctionArgument]:
        """
        Returns
        -------
        All function arguments used within the SyntaxTree
        """
        function_arguments: Set[FunctionArgument] = set()
        for token in self.ast:
            if isinstance(token, FunctionArgument):
                function_arguments.add(token)
            elif isinstance(token, VariableDependency):
                function_arguments.update(token.function_arguments)

        return function_arguments

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
