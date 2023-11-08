from abc import ABC
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import Generic
from typing import TypeVar

T = TypeVar("T")
NumericT = TypeVar("NumericT", bound=int | float)


class ArgumentType(ABC):
    pass


class Resolvable_0(ABC):
    pass


class Resolvable_1(ABC):
    pass


class Resolvable_2(ABC):
    pass


@dataclass(frozen=True)
class Resolvable(Resolvable_0, Resolvable_1, Resolvable_2, ABC):
    value: Any

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class ResolvableT(Resolvable, ABC, Generic[T]):
    value: T


@dataclass(frozen=True)
class Numeric(ResolvableT[NumericT], ABC, Generic[NumericT]):
    pass


@dataclass(frozen=True)
class Integer(Numeric[int], ArgumentType):
    pass


@dataclass(frozen=True)
class Float(Numeric[float], ArgumentType):
    pass


@dataclass(frozen=True)
class Boolean(ResolvableT[bool], ArgumentType):
    pass


@dataclass(frozen=True)
class String(ResolvableT[str], ArgumentType):
    pass


@dataclass(frozen=True)
class Map(Resolvable, ArgumentType):
    value: Dict[Resolvable, Resolvable]

    def __str__(self) -> str:
        return f"[{', '.join([val.value for val in self.value])}]"
