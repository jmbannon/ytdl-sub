from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Set

from ytdl_sub.script.types.resolvable import ArgumentType
from ytdl_sub.script.types.resolvable import FutureResolvable
from ytdl_sub.script.types.resolvable import NonHashable
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import ResolvableToJson
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency


@dataclass(frozen=True)
class Array(NonHashable):
    value: List[Resolvable]

    @classmethod
    def type_name(cls) -> str:
        return "Array"


@dataclass(frozen=True)
class UnresolvedArray(Array, VariableDependency, FutureResolvable):
    value: List[ArgumentType]

    @property
    def variables(self) -> Set[Variable]:
        variables: Set[Variable] = set()
        for arg in self.value:
            if isinstance(arg, Variable):
                variables.add(arg)
            elif isinstance(arg, VariableDependency):
                variables.update(arg.variables)

        return variables

    @property
    def function_arguments(self) -> Set[FunctionArgument]:
        variables: Set[FunctionArgument] = set()
        for arg in self.value:
            if isinstance(arg, FunctionArgument):
                variables.add(arg)
            elif isinstance(arg, VariableDependency):
                variables.update(arg.function_arguments)

        return variables

    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        return ResolvedArray(
            [
                self._resolve_argument_type(
                    arg=arg,
                    resolved_variables=resolved_variables,
                    custom_functions=custom_functions,
                )
                for arg in self.value
            ]
        )


@dataclass(frozen=True)
class ResolvedArray(Array, ResolvableToJson):
    pass
