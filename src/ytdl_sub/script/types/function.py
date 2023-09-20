from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Set
from typing import Union
from typing import final

from ytdl_sub.script.functions import Functions
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.utils.exceptions import StringFormattingException

ArgumentType = Union[Integer, Float, String, Boolean, Variable, "Function"]


@dataclass(frozen=True)
class VariableDependency(ABC):
    @property
    @abstractmethod
    def variables(self) -> Set[Variable]:
        raise NotImplemented()

    @abstractmethod
    def resolve(self, resolved_variables: Dict[Variable, Resolvable]) -> str:
        raise NotImplemented()

    @final
    def has_variable_dependency(self, resolved_variables: Dict[Variable, Resolvable]) -> bool:
        """
        Returns
        -------
        True if variable dependency. False otherwise.
        """
        return self.variables.issubset(set(resolved_variables.keys()))


@dataclass(frozen=True)
class Function(VariableDependency):
    name: str
    args: List[ArgumentType]

    def __post_init__(self):
        # TODO: Figure out resolution via introspecting args and outputs of function
        try:
            getattr(Functions, self.name)
        except AttributeError:
            raise StringFormattingException(f"Function name {self.name} does not exist")

    @property
    def variables(self) -> Set[Variable]:
        """
        Returns
        -------
        All variables used within the function
        """
        variables: Set[Variable] = set()
        for arg in self.args:
            if isinstance(arg, Variable):
                variables.add(arg)
            elif isinstance(arg, Function):
                variables.update(arg.variables)

        return variables

    def resolve(self, resolved_variables: Dict[Variable, Resolvable]) -> Resolvable:
        raise NotImplemented()
