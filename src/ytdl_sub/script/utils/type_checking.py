# pylint: disable=missing-raises-doc
import inspect
from dataclasses import dataclass
from inspect import FullArgSpec
from typing import Callable
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import Union
from typing import get_origin

from ytdl_sub.script.types.resolvable import Argument
from ytdl_sub.script.types.resolvable import BuiltInFunctionType
from ytdl_sub.script.types.resolvable import FutureResolvable
from ytdl_sub.script.types.resolvable import Lambda
from ytdl_sub.script.types.resolvable import LambdaReduce
from ytdl_sub.script.types.resolvable import LambdaThree
from ytdl_sub.script.types.resolvable import LambdaTwo
from ytdl_sub.script.types.resolvable import NamedCustomFunction
from ytdl_sub.script.types.resolvable import NamedType
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import UNREACHABLE

LambdaT = TypeVar("LambdaT", bound=Lambda)


def is_union(arg_type: Type) -> bool:
    """
    Returns
    -------
    True if typing is Union. False otherwise.
    """
    return get_origin(arg_type) is Union


def is_optional(arg_type: Type) -> bool:
    """
    Returns
    -------
    True if typing is Optional. False otherwise.
    """
    return is_union(arg_type) and type(None) in arg_type.__args__


def get_optional_type(optional_type: Type) -> Type[NamedType]:
    """
    Returns
    -------
    Type within the Optional[Type]
    """
    return [arg for arg in optional_type.__args__ if arg != type(None)][0]


def _is_union_compatible(
    arg_type: Type[NamedType],
    expected_union_type: Type[Resolvable | Optional[Resolvable]],
) -> bool:
    if issubclass(arg_type, (NamedCustomFunction, Variable)):
        return True  # custom-function/variable can be anything, so pass for now

    # if the input arg is a union, do a direct comparison
    if is_union(arg_type):
        return arg_type == expected_union_type

    # otherwise, iterate the union to see if it's compatible
    for union_type in expected_union_type.__args__:
        if issubclass(arg_type, union_type):
            return True

    return False


def _is_type_compatible(
    arg_type: Type[NamedType],
    expected_arg_type: Type[Resolvable | Optional[Resolvable]],
) -> bool:
    """
    Returns
    -------
    True if arg is compatible with expected_arg_type. False otherwise.
    """
    if is_union(expected_arg_type):
        return _is_union_compatible(arg_type=arg_type, expected_union_type=expected_arg_type)

    # If the input is a union and the expected type is not, see if
    # each possible union input is compatible with the expected type
    if is_union(arg_type):
        for union_type in arg_type.__args__:
            if not _is_type_compatible(union_type, expected_arg_type):
                return False
    elif issubclass(arg_type, (NamedCustomFunction, Variable)):
        return True  # custom-function/variable can be anything, so pass for now
    elif issubclass(arg_type, Lambda) and issubclass(expected_arg_type, arg_type):
        # lambda, check if expected_arg_type is a subclass
        # Do not return on just that to also allow lambdas to be returned as
        # ReturnableArguments (i.e in an %if statement)
        return True

    elif not issubclass(arg_type, expected_arg_type):
        return False

    return True


def is_type_compatible(
    arg: NamedType,
    expected_arg_type: Type[Resolvable | Optional[Resolvable]],
) -> bool:
    """
    Returns
    -------
    True if arg is compatible with expected_arg_type. False otherwise.
    """
    arg_type: Type[NamedType] = arg.__class__
    if isinstance(arg, BuiltInFunctionType):
        arg_type = arg.output_type()  # built-in function
    elif isinstance(arg, FutureResolvable):
        arg_type = arg.future_resolvable_type()

    return _is_type_compatible(arg_type, expected_arg_type)


@dataclass(frozen=True)
class FunctionSpec:
    function_name: str
    return_type: Type[Resolvable]
    arg_names: List[str]
    args: Optional[List[Type[Resolvable | Optional[Resolvable]]]] = None
    varargs: Optional[Type[Resolvable]] = None

    def __post_init__(self):
        assert (self.args is None) ^ (self.varargs is None)

    def _is_args_compatible(self, input_args: List[Argument]) -> bool:
        assert self.args is not None

        if len(input_args) > len(self.args):
            return False

        for idx, arg in enumerate(self.args):
            input_arg = input_args[idx] if idx < len(input_args) else None
            if not is_type_compatible(arg=input_arg, expected_arg_type=arg):
                return False

        return True

    def _is_varargs_compatible(self, input_args: List[Argument]) -> bool:
        """
        Returns
        -------
        True if the input args are compatible with the spec's varargs. False otherwise.
        """
        assert self.varargs is not None

        for input_arg in input_args:
            if not is_type_compatible(arg=input_arg, expected_arg_type=self.varargs):
                return False

        return True

    def is_compatible(self, input_args: List[Argument]) -> bool:
        """
        Returns
        -------
        True if input_args is compatible. False otherwise.
        """
        if self.args is not None:
            return self._is_args_compatible(input_args=input_args)
        if self.varargs is not None:
            return self._is_varargs_compatible(input_args=input_args)

        raise UNREACHABLE  # TODO: functions with no args

    def is_num_args_compatible(self, num_input_args: int) -> bool:
        """
        Returns
        -------
        True if the number of input args is compatible with the function spec. False otherwise.
        """
        if self.args is not None:
            return self.num_required_args <= num_input_args <= len(self.args)
        return True  # varargs can take any number

    @property
    def num_required_args(self) -> int:
        """
        Returns
        -------
        The minimum number of args required to call the function.
        """
        if self.args is not None:
            return sum(1 for arg in self.args if not is_optional(arg))
        return 0  # varargs can take any number

    def conditional_arg_indices(self, num_input_args: int) -> List[int]:
        """
        Returns
        -------
        If the function is conditional, return the indices of the arguments that
        return for different branches.
        """
        if self.function_name == "if":
            return [1, 2]  # true, false
        if self.function_name == "elif":
            # if, retA, elif, retB, retElse
            return list(range(1, num_input_args, 2)) + [num_input_args - 1]
        if self.function_name == "if_passthrough":
            return [0, 1]  # true-passthrough, false-passthrough
        if self.function_name in ("assert", "assert_eq", "assert_ne"):
            return [0]
        if self.function_name == "assert_then":
            return [1]
        return []

    @property
    def is_lambda_reduce_function(self) -> Optional[Type[LambdaReduce]]:
        """
        Returns
        -------
        True if the function is a Lambda-reduce function. False otherwise.
        """
        return LambdaReduce if LambdaReduce in (self.args or []) else None

    @property
    def is_lambda_function(self) -> Optional[Type[Lambda | LambdaTwo | LambdaThree]]:
        """
        Returns
        -------
        True if the function is a Lambda function (excluding reduce). False otherwise.
        """
        if LambdaThree in (self.args or []):
            return LambdaThree
        if LambdaTwo in (self.args or []):
            return LambdaTwo
        if Lambda in (self.args or []):
            return Lambda
        return None

    @property
    def is_lambda_like(self) -> Optional[Type[LambdaT]]:
        """
        Returns
        -------
        True if the function is a Lambda type (including reduce).
        """
        if l_type := self.is_lambda_reduce_function:
            return l_type
        if l_type := self.is_lambda_function:
            return l_type
        return None

    @classmethod
    def _to_human_readable_name(cls, python_type: Type[NamedType] | Type[Union[NamedType]]) -> str:
        if is_optional(python_type):
            return f"Optional[{cls._to_human_readable_name(get_optional_type(python_type))}]"
        if is_union(python_type):
            args = ", ".join(
                sorted(cls._to_human_readable_name(arg) for arg in python_type.__args__)
            )
            return f"Union[{args}]"
        return python_type.type_name()

    def human_readable_input_args(self) -> str:
        """
        Returns
        -------
        input arg string in human-readable format
        """
        if self.args is not None:
            args = ", ".join(
                f"{name}: {self._to_human_readable_name(type_)}"
                for name, type_ in zip(self.arg_names, self.args)
            )
        elif self.varargs is not None:
            args = f"{self.arg_names[0]}: {self._to_human_readable_name(self.varargs)}, ..."
        else:
            args = ""
        return f"({args})"

    def human_readable_output_type(self) -> str:
        """
        Returns
        -------
        output type string in human-readable format
        """
        return self._to_human_readable_name(self.return_type)

    @classmethod
    def from_callable(cls, name: str, callable_ref: Callable[..., Resolvable]) -> "FunctionSpec":
        """
        Returns
        -------
        FunctionSpec from a built-in function.
        """
        arg_spec: FullArgSpec = inspect.getfullargspec(callable_ref)
        if arg_spec.varargs:
            return FunctionSpec(
                function_name=name,
                return_type=arg_spec.annotations["return"],
                arg_names=[arg_spec.varargs],
                varargs=arg_spec.annotations[arg_spec.varargs],
            )

        return FunctionSpec(
            function_name=name,
            return_type=arg_spec.annotations["return"],
            arg_names=arg_spec.args,
            args=[arg_spec.annotations[arg_name] for arg_name in arg_spec.args],
        )
