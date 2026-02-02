import itertools
from abc import ABC
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Type

from ytdl_sub.script.types.resolvable import Argument
from ytdl_sub.script.types.resolvable import FutureResolvable
from ytdl_sub.script.types.resolvable import Hashable
from ytdl_sub.script.types.resolvable import NonHashable
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import ResolvableToJson
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency
from ytdl_sub.script.utils.exceptions import KeyNotHashableRuntimeException


@dataclass(frozen=True)
class _Map(NonHashable, ABC):
    value: Dict[Hashable, Resolvable]

    @classmethod
    def type_name(cls) -> str:
        return "Map"


@dataclass(frozen=True)
class UnresolvedMap(_Map, VariableDependency, FutureResolvable):
    value: Dict[Argument, Argument]

    @property
    def iterable_arguments(self) -> List[Argument]:
        return list(itertools.chain(*self.value.items()))

    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, VariableDependency],
    ) -> Resolvable:
        output: Dict[Hashable, Resolvable] = {}
        for key, value in self.value.items():
            resolved_key = self._resolve_argument_type(
                arg=key, resolved_variables=resolved_variables, custom_functions=custom_functions
            )
            if not isinstance(resolved_key, Hashable):
                raise KeyNotHashableRuntimeException(
                    f"Tried to use {resolved_key.type_name()} as a Map key, but it is not hashable."
                )

            output[resolved_key] = self._resolve_argument_type(
                arg=value, resolved_variables=resolved_variables, custom_functions=custom_functions
            )

        return Map(output)

    def partial_resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        unresolved_variables: Dict[Variable, Argument],
        custom_functions: Dict[str, VariableDependency],
    ) -> Argument | Resolvable:
        maybe_resolvable_keys, is_keys_resolvable = VariableDependency.try_partial_resolve(
            args=self.value.keys(),
            resolved_variables=resolved_variables,
            unresolved_variables=unresolved_variables,
            custom_functions=custom_functions,
        )

        maybe_resolvable_values, is_values_resolvable = VariableDependency.try_partial_resolve(
            args=self.value.values(),
            resolved_variables=resolved_variables,
            unresolved_variables=unresolved_variables,
            custom_functions=custom_functions,
        )

        out = UnresolvedMap(value=dict(zip(maybe_resolvable_keys, maybe_resolvable_values)))
        if is_keys_resolvable and is_values_resolvable:
            return out.resolve(
                resolved_variables=resolved_variables,
                custom_functions=custom_functions,
            )

        return out

    def future_resolvable_type(self) -> Type[Resolvable]:
        return Map


@dataclass(frozen=True)
class Map(_Map, ResolvableToJson):
    @property
    def native(self) -> Any:
        return {key.native: value.native for key, value in self.value.items()}
