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


class NamedType(ABC):
    @classmethod
    def type_name(cls) -> str:
        """
        Returns
        -------
        The type name to present to users. Defaults to the class name.
        """
        return cls.__name__


class ArgumentType(NamedType, ABC):
    """
    Any possible argument type that has not been resolved yet
    """


class AnyTypeReturnable(NamedType, ABC):
    """
    AnyType to express generics in functions that are part of the return type
    """


class AnyTypeReturnableA(NamedType, ABC):
    """
    AnyType to express generics in functions when more than one are present (i.e. `if`)
    """


class AnyTypeReturnableB(NamedType, ABC):
    """
    AnyType to express generics in functions when more than one are present (i.e. `if`)
    """


class AnyType(ArgumentType, AnyTypeReturnable, AnyTypeReturnableA, AnyTypeReturnableB, ABC):
    """
    Human-readable name for FutureResolvable
    """

    value: Any


class FutureResolvable(AnyType, ABC):
    """
    Type that will be resolved in the future
    """


@dataclass(frozen=True)
class Resolvable(AnyType, ABC):
    def __str__(self) -> str:
        return str(self.value)


class Hashable(Resolvable, ABC):
    pass


class NonHashable(ABC):
    pass


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


@dataclass(frozen=True)
class FunctionType(ArgumentType, ABC):
    name: str
    args: List[ArgumentType]


@dataclass(frozen=True)
class TypeHintedFunctionType(FunctionType, ABC):
    @abstractmethod
    def output_type(self) -> Type[Resolvable]:
        pass


@dataclass(frozen=True)
class Lambda(Resolvable):
    function_name: str
