from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Generic
from typing import TypeVar

T = TypeVar("T")
NumericT = TypeVar("NumericT", bound=int | float)


@dataclass(frozen=True)
class Resolvable(ABC):
    @abstractmethod
    def resolve(self) -> str:
        ...


@dataclass(frozen=True)
class ResolvableT(Resolvable, Generic[T]):
    value: T

    def resolve(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Numeric(ResolvableT[NumericT], ABC, Generic[NumericT]):
    pass


@dataclass(frozen=True)
class Integer(ResolvableT[int]):
    pass


@dataclass(frozen=True)
class Float(ResolvableT[float]):
    pass


@dataclass(frozen=True)
class Boolean(ResolvableT[bool]):
    pass


@dataclass(frozen=True)
class String(ResolvableT[str]):
    pass
