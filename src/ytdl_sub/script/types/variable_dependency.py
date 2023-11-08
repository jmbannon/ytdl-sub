from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import Set
from typing import final

from ytdl_sub.script.types.resolvable import ArgumentType
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.utils.exceptions import StringFormattingException


@dataclass(frozen=True)
class VariableDependency(ABC):
    @property
    @abstractmethod
    def variables(self) -> Set[Variable]:
        raise NotImplemented()

    @abstractmethod
    def resolve(self, resolved_variables: Dict[Variable, Resolvable]) -> Resolvable:
        raise NotImplemented()

    def _resolve_argument_type(
        self, resolved_variables: Dict[Variable, Resolvable], arg: ArgumentType
    ) -> Resolvable:
        if isinstance(arg, Resolvable):
            return arg
        if isinstance(arg, Variable):
            if arg not in resolved_variables:
                raise StringFormattingException("should never reach@")
            return resolved_variables[arg]
        if isinstance(arg, VariableDependency):
            return arg.resolve(resolved_variables)

        assert False, "never reach here"

    @final
    def has_variable_dependency(self, resolved_variables: Dict[Variable, Resolvable]) -> bool:
        """
        Returns
        -------
        True if variable dependency. False otherwise.
        """
        return not self.variables.issubset(set(resolved_variables.keys()))
