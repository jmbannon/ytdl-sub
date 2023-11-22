from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import Set
from typing import final

from ytdl_sub.script.types.resolvable import ArgumentType
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.variable import FunctionArgument
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import UNREACHABLE
from ytdl_sub.utils.exceptions import StringFormattingException


@dataclass(frozen=True)
class VariableDependency(ABC):
    @classmethod
    def _variables(cls, *args: ArgumentType) -> Set[Variable]:
        output: Set[Variable] = set()
        for arg in args:
            if isinstance(arg, Variable):
                output.add(arg)
            elif isinstance(arg, VariableDependency):
                output.update(arg.variables)

        return output

    @classmethod
    def _function_arguments(cls, *args: ArgumentType) -> Set[FunctionArgument]:
        output: Set[FunctionArgument] = set()
        for arg in args:
            if isinstance(arg, FunctionArgument):
                output.add(arg)
            elif isinstance(arg, VariableDependency):
                output.update(arg.function_arguments)

        return output

    @property
    @abstractmethod
    def variables(self) -> Set[Variable]:
        pass

    @property
    @abstractmethod
    def function_arguments(self) -> Set[FunctionArgument]:
        pass

    @abstractmethod
    def resolve(
        self,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        pass

    @classmethod
    def _resolve_argument_type(
        cls,
        arg: ArgumentType,
        resolved_variables: Dict[Variable, Resolvable],
        custom_functions: Dict[str, "VariableDependency"],
    ) -> Resolvable:
        if isinstance(arg, Resolvable):
            return arg
        if isinstance(arg, Variable):
            if arg not in resolved_variables:
                raise StringFormattingException("should never reach@")
            return resolved_variables[arg]
        if isinstance(arg, VariableDependency):
            return arg.resolve(
                resolved_variables=resolved_variables, custom_functions=custom_functions
            )

        raise UNREACHABLE

    @final
    def has_variable_dependency(self, resolved_variables: Dict[Variable, Resolvable]) -> bool:
        """
        Returns
        -------
        True if variable dependency. False otherwise.
        """
        return not self.variables.issubset(set(resolved_variables.keys()))
