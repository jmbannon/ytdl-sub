from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Set

from ytdl_sub.script.types.resolvable import ArgumentType
from ytdl_sub.script.types.resolvable import Hashable
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency
from ytdl_sub.utils.exceptions import StringFormattingException


@dataclass(frozen=True)
class Map:
    value: Dict[Hashable, Resolvable]


@dataclass(frozen=True)
class UnresolvedMap(Map, VariableDependency, ArgumentType):
    value: Dict[ArgumentType, ArgumentType]

    @property
    def variables(self) -> Set[Variable]:
        output: Set[Variable] = set()
        for key, value in self.value.items():
            if isinstance(key, Variable):
                output.add(key)
            if isinstance(value, Variable):
                output.add(key)
        return output

    def resolve(self, resolved_variables: Dict[Variable, Resolvable]) -> Resolvable:
        output: Dict[Hashable, Resolvable] = {}
        for key, value in self.value.items():
            resolved_key = self._resolve_argument_type(
                resolved_variables=resolved_variables, arg=key
            )
            if not isinstance(resolved_key, Hashable):
                raise StringFormattingException("key is not hashable")

            output[resolved_key] = self._resolve_argument_type(
                resolved_variables=resolved_variables, arg=value
            )

        return ResolvedMap(output)


@dataclass(frozen=True)
class ResolvedMap(Map, Resolvable):
    pass
