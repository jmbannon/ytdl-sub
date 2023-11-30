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
class ValueArgument(Argument, ABC):
    """
    Argument that has a value
    """

    value: Any


@dataclass(frozen=True)
class NamedArgument(Argument, ABC):
    """
    Argument that has an explicit name (i.e. custom function or variable)
    """

    name: str


@dataclass(frozen=True)
class ReturnableArgument(ValueArgument, NamedType, ABC):
    """
    AnyType to express generics in functions that are part of the return type
    """


@dataclass(frozen=True)
class ReturnableArgumentA(ValueArgument, NamedType, ABC):
    """
    AnyType to express generics in functions when more than one are present (i.e. `if`)
    """


@dataclass(frozen=True)
class ReturnableArgumentB(ValueArgument, NamedType, ABC):
    """
    AnyType to express generics in functions when more than one are present (i.e. `if`)
    """


@dataclass(frozen=True)
class AnyArgument(ReturnableArgument, ReturnableArgumentA, ReturnableArgumentB, ABC):
    """
    Human-readable name for FutureResolvable
    """


@dataclass(frozen=True)
class Resolvable(AnyArgument, ABC):
    def __str__(self) -> str:
        return str(self.value)

    @property
    def native(self) -> Any:
        return self.value


@dataclass(frozen=True)
class Hashable(Resolvable, ABC):
    pass


@dataclass(frozen=True)
class NonHashable(ABC):
    pass


@dataclass(frozen=True)
class ResolvableToJson(Resolvable, ABC):
    def __str__(self):
        return json.dumps(self.native)


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
class NamedCustomFunction(NamedArgument, ABC):
    pass


@dataclass(frozen=True)
class ParsedCustomFunction(NamedCustomFunction):
    num_input_args: int


@dataclass(frozen=True)
class FunctionType(NamedArgument, ABC):
    args: List[Argument]


@dataclass(frozen=True)
class BuiltInFunctionType(FunctionType, ABC):
    @abstractmethod
    def output_type(self) -> Type[Resolvable]:
        pass


@dataclass(frozen=True)
class Lambda(Resolvable):
    value: str

    def native(self) -> Any:
        return f"%{self.value}"

    @classmethod
    def num_input_args(cls) -> int:
        return 1


@dataclass(frozen=True)
class Lambda2(Lambda):
    """
    Type-hinting for functions that apply lambdas with two inputs per element
    """

    @classmethod
    def num_input_args(cls) -> int:
        return 2
