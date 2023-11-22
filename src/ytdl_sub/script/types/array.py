from dataclasses import dataclass
from typing import Dict
from typing import List

from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Argument
from ytdl_sub.script.types.resolvable import NonHashable
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import ResolvableToJson
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency


@dataclass(frozen=True)
class Array(NonHashable):
    value: List[Resolvable]

    @classmethod
    def type_name(cls) -> str:
        return "Array"


@dataclass(frozen=True)
class UnresolvedArray(Array, VariableDependency, AnyArgument):
    value: List[Argument]

    @property
    def _iterable_arguments(self) -> List[Argument]:
        return self.value

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
