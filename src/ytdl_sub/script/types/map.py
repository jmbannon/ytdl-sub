from dataclasses import dataclass
from typing import Dict
from typing import Set

from ytdl_sub.script.types.resolvable import ArgumentType
from ytdl_sub.script.types.resolvable import FutureResolvable
from ytdl_sub.script.types.resolvable import Hashable
from ytdl_sub.script.types.resolvable import NonHashable
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import ResolvableToJson
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.types.variable_dependency import VariableDependency
from ytdl_sub.utils.exceptions import StringFormattingException


@dataclass(frozen=True)
class Map(NonHashable):
    value: Dict[Hashable, Resolvable]

    @classmethod
    def type_name(cls) -> str:
        return "Map"


@dataclass(frozen=True)
class UnresolvedMap(Map, VariableDependency, FutureResolvable):
    value: Dict[ArgumentType, ArgumentType]

    @property
    def variables(self) -> Set[Variable]:
        output: Set[Variable] = set()
        for key, value in self.value.items():
            if isinstance(key, Variable):
                output.add(key)
            elif isinstance(key, VariableDependency):
                output.update(key.variables)

            if isinstance(value, Variable):
                output.add(key)
            elif isinstance(value, VariableDependency):
                output.update(value.variables)

        return output

    @property
    def function_arguments(self) -> Set[FunctionArgument]:
        output: Set[FunctionArgument] = set()
        for key, value in self.value.items():
            if isinstance(key, FunctionArgument):
                output.add(key)
            elif isinstance(key, VariableDependency):
                output.update(key.function_arguments)

            if isinstance(value, FunctionArgument):
                output.add(key)
            elif isinstance(value, VariableDependency):
                output.update(value.function_arguments)

        return output

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
                raise StringFormattingException("key is not hashable")

            output[resolved_key] = self._resolve_argument_type(
                arg=value, resolved_variables=resolved_variables, custom_functions=custom_functions
            )

        return ResolvedMap(output)


@dataclass(frozen=True)
class ResolvedMap(Map, ResolvableToJson):
    pass
