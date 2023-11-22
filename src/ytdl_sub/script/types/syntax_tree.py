from dataclasses import dataclass
from typing import Dict
from typing import List

from ytdl_sub.script.types.resolvable import ArgumentType
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency


@dataclass(frozen=True)
class SyntaxTree(VariableDependency):
    ast: List[ArgumentType]

    @property
    def _iterable_arguments(self) -> List[ArgumentType]:
        return self.ast

    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, VariableDependency],
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
