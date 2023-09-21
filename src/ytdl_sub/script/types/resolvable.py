from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import Generic
from typing import List
from typing import TypeVar

T = TypeVar("T")
NumericT = TypeVar("NumericT", bound=int | float)


@dataclass(frozen=True)
class Resolvable(ABC):
    value: Any

    @abstractmethod
    def resolve(self) -> str:
        ...


@dataclass(frozen=True)
class ResolvableT(Resolvable, ABC, Generic[T]):
    value: T

    def resolve(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Numeric(ResolvableT[NumericT], ABC, Generic[NumericT]):
    pass


@dataclass(frozen=True)
class Integer(Numeric[int]):
    pass


@dataclass(frozen=True)
class Float(Numeric[float]):
    pass


@dataclass(frozen=True)
class Boolean(ResolvableT[bool]):
    pass


@dataclass(frozen=True)
class String(ResolvableT[str]):
    pass


@dataclass(frozen=True)
class _List(Resolvable, Generic[T], ABC):
    value: List[T]

    def resolve(self) -> str:
        return f"[{', '.join([str(val) for val in self.value])}]"


@dataclass(frozen=True)
class StringList(_List[String]):
    pass
