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
    Human-readable name for Resolvable
    """


@dataclass(frozen=True)
class Resolvable(AnyArgument, ABC):
    """
    A type that is resolved into a native Python type (and have no dependencies to other types).
    """

    def __str__(self) -> str:
        return str(self.value)

    @property
    def native(self) -> Any:
        """
        Returns
        -------
        The resolvable in its native form
        """
        return self.value


@dataclass(frozen=True)
class FutureResolvable(AnyArgument, ABC):
    """
    Used when parsing, it is an unresolved type that will eventually resolve to a known type
    (i.e. Maps, Arrays)
    """

    @abstractmethod
    def future_resolvable_type(self) -> Type[Resolvable]:
        """
        The resolvable type that this type is known to turn into
        """


@dataclass(frozen=True)
class Hashable(Resolvable, ABC):
    """
    Resolvable type that can be used as hashes (i.e. in Maps)
    """


@dataclass(frozen=True)
class NonHashable(NamedType, ABC):
    """
    Type that is known to never be hashable.
    """


@dataclass(frozen=True)
class ResolvableToJson(Resolvable, ABC):
    """
    Types whose string values should be resolved to JSON (i.e. Maps, Arrays)
    """

    def __str__(self):
        return json.dumps(self.native)


@dataclass(frozen=True)
class ResolvableT(Hashable, ABC, Generic[T]):
    """
    Resolvable types that resolve to the generic T
    """

    value: T


@dataclass(frozen=True)
class Numeric(ResolvableT[NumericT], ABC, Generic[NumericT]):
    """
    Resolvable numeric types (int/float)
    """


@dataclass(frozen=True)
class Integer(Numeric[int], Argument):
    """
    Resolved Integer type
    """


@dataclass(frozen=True)
class Float(Numeric[float], Argument):
    """
    Resolved float type
    """


@dataclass(frozen=True)
class Boolean(ResolvableT[bool], Argument):
    """
    Resolved bool type
    """

    def __str__(self):
        # makes it JSON friendly
        return str(self.value).lower()


@dataclass(frozen=True)
class String(ResolvableT[str], Argument):
    """
    Resolved String type
    """


@dataclass(frozen=True)
class NamedCustomFunction(NamedArgument, ABC):
    """
    A custom function with a defined name (but unknown args)
    """


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
        """
        Returns
        -------
        The known Resolvable type that a BuiltInFunction will output
        """


@dataclass(frozen=True)
class Lambda(Resolvable):
    value: str

    @property
    def native(self) -> Any:
        return f"%{self.value}"

    @classmethod
    def num_input_args(cls) -> int:
        """
        Returns
        -------
        The number of input args the Lambda function takes
        """
        return 1


@dataclass(frozen=True)
class LambdaTwo(Lambda):
    """
    Type-hinting for functions that apply lambdas with two inputs per element
    """

    @classmethod
    def num_input_args(cls) -> int:
        return 2


@dataclass(frozen=True)
class LambdaThree(Lambda):
    """
    Type-hinting for functions that apply lambdas with three inputs per element
    """

    @classmethod
    def num_input_args(cls) -> int:
        return 3


@dataclass(frozen=True)
class LambdaReduce(LambdaTwo):
    """
    Type-hinting for functions that apply a reduce-operation using a lambda (two arguments)
    """
