from abc import ABC
from dataclasses import dataclass
from typing import Any
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


class Hashable(Resolvable, ABC):
    pass


@dataclass(frozen=True)
class ResolvableT(Hashable, ABC, Generic[T]):
    value: T


@dataclass(frozen=True)
class Numeric(ResolvableT[NumericT], Hashable, ABC, Generic[NumericT]):
    pass


@dataclass(frozen=True)
class Integer(Numeric[int], ArgumentType):
    pass


@dataclass(frozen=True)
class Float(Numeric[float], ArgumentType):
    pass


@dataclass(frozen=True)
class Boolean(ResolvableT[bool], Hashable, ArgumentType):
    pass


@dataclass(frozen=True)
class String(ResolvableT[str], Hashable, ArgumentType):
    pass
