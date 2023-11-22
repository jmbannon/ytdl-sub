import json
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from typing import Generic
from typing import List
from typing import Type
from typing import TypeVar

T = TypeVar("T")
NumericT = TypeVar("NumericT", bound=int | float)


@dataclass(frozen=True)
class NamedType(ABC):
    @classmethod
    def type_name(cls) -> str:
        """
        Returns
        -------
        The type name to present to users. Defaults to the class name.
        """
        return cls.__name__


@dataclass(frozen=True)
class Argument(NamedType, ABC):
    """
    Any possible argument type that has not been resolved yet
    """


@dataclass(frozen=True)
class NamedArgument(Argument, ABC):
    """
    Argument that has an explicit name (i.e. custom function or variable)
    """

    name: str


@dataclass(frozen=True)
class ReturnableArgument(NamedType, ABC):
    """
    AnyType to express generics in functions that are part of the return type
    """


@dataclass(frozen=True)
class ReturnableArgumentA(NamedType, ABC):
    """
    AnyType to express generics in functions when more than one are present (i.e. `if`)
    """


@dataclass(frozen=True)
class ReturnableArgumentB(NamedType, ABC):
    """
    AnyType to express generics in functions when more than one are present (i.e. `if`)
    """


@dataclass(frozen=True)
class AnyArgument(Argument, ReturnableArgument, ReturnableArgumentA, ReturnableArgumentB, ABC):
    """
    Human-readable name for FutureResolvable
    """

    value: Any


@dataclass(frozen=True)
class Resolvable(AnyArgument, ABC):
    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Hashable(Resolvable, ABC):
    pass


@dataclass(frozen=True)
class NonHashable(ABC):
    pass


@dataclass(frozen=True)
class ResolvableToJson(Resolvable, ABC):
    @classmethod
    def _to_native(cls, to_convert: Resolvable) -> Any:
        if isinstance(to_convert.value, list):
            return [cls._to_native(val) for val in to_convert.value]
        if isinstance(to_convert.value, dict):
            return {
                cls._to_native(key): cls._to_native(value)
                for key, value in to_convert.value.items()
            }
        return to_convert.value

    def __str__(self):
        return json.dumps(self._to_native(self))


@dataclass(frozen=True)
class ResolvableT(Hashable, ABC, Generic[T]):
    value: T


@dataclass(frozen=True)
class Numeric(ResolvableT[NumericT], Hashable, ABC, Generic[NumericT]):
    pass


@dataclass(frozen=True)
class Integer(Numeric[int], Argument):
    pass


@dataclass(frozen=True)
class Float(Numeric[float], Argument):
    pass


@dataclass(frozen=True)
class Boolean(ResolvableT[bool], Hashable, Argument):
    pass


@dataclass(frozen=True)
class String(ResolvableT[str], Hashable, Argument):
    pass


@dataclass(frozen=True)
class NamedCustomFunction(Argument, ABC):
    name: str


@dataclass(frozen=True)
class FunctionType(NamedArgument, ABC):
    args: List[Argument]


@dataclass(frozen=True)
class TypeHintedFunctionType(FunctionType, ABC):
    @abstractmethod
    def output_type(self) -> Type[Resolvable]:
        pass


@dataclass(frozen=True)
class Lambda(Resolvable):
    value: str
