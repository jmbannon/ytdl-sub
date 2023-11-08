from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Set

from ytdl_sub.script.types.resolvable import ArgumentType
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency


@dataclass(frozen=True)
class Array:
    value: List[Resolvable]


@dataclass(frozen=True)
class UnresolvedArray(Array, VariableDependency, ArgumentType):
    value: List[ArgumentType]

    @property
    def variables(self) -> Set[Variable]:
        return {value for value in self.value if isinstance(value, Variable)}

    def resolve(self, resolved_variables: Dict[Variable, Resolvable]) -> Resolvable:
        return ResolvedArray(
            [
                self._resolve_argument_type(resolved_variables=resolved_variables, arg=arg)
                for arg in self.value
            ]
        )


@dataclass(frozen=True)
class ResolvedArray(Array, Resolvable):
    pass
