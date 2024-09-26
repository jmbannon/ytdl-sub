from abc import ABC
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Type

from ytdl_sub.script.types.resolvable import Argument
from ytdl_sub.script.types.resolvable import FutureResolvable
from ytdl_sub.script.types.resolvable import NonHashable
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import ResolvableToJson
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency


@dataclass(frozen=True)
class _Array(NonHashable, ABC):
    value: List[Resolvable]

    @classmethod
    def type_name(cls) -> str:
        return "Array"


@dataclass(frozen=True)
class UnresolvedArray(_Array, VariableDependency, FutureResolvable):
    value: List[Argument]

    @property
    def _iterable_arguments(self) -> List[Argument]:
        return self.value

    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        return Array(
            [
                self._resolve_argument_type(
                    arg=arg,
                    resolved_variables=resolved_variables,
                    custom_functions=custom_functions,
                )
                for arg in self.value
            ]
        )

    def future_resolvable_type(self) -> Type[Resolvable]:
        return Array


@dataclass(frozen=True)
class Array(_Array, ResolvableToJson):
    @property
    def native(self) -> Any:
        return [val.native for val in self.value]

    def __len__(self) -> int:
        return len(self.value)
