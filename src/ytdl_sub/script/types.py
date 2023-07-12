from dataclasses import dataclass
from typing import List
from typing import Set
from typing import Union


@dataclass(frozen=True)
class Integer:
    value: int


@dataclass(frozen=True)
class Float:
    value: float


@dataclass(frozen=True)
class Boolean:
    value: bool


@dataclass(frozen=True)
class String:
    value: str


@dataclass(frozen=True)
class Variable:
    name: str


NumericType = Union[Integer, Float]
ArgumentType = Union[Integer, Float, String, Boolean, Variable, "Function"]


@dataclass(frozen=True)
class Function:
    name: str
    args: List[ArgumentType]

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
                variables.union(arg.variables)

        return variables


@dataclass(frozen=True)
class LiteralString:
    value: str


@dataclass(frozen=True)
class SyntaxTree:
    ast: List[LiteralString | Variable | Function]

    @property
    def variables(self) -> Set[Variable]:
        variables: Set[Variable] = set()
        for token in self.ast:
            if isinstance(token, Variable):
                variables.add(token)
            elif isinstance(token, Function):
                variables.union(token.variables)

        return variables
