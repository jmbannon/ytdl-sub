from dataclasses import dataclass
from typing import List
from typing import Optional
from typing import Type
from typing import Union
from typing import get_origin

from ytdl_sub.script.types.resolvable import ArgumentType
from ytdl_sub.script.types.resolvable import FunctionType
from ytdl_sub.script.types.resolvable import NamedType
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import TypeHintedFunctionType
from ytdl_sub.script.types.variable import Variable
from ytdl_sub.script.utils.exceptions import UNREACHABLE

# pylint: disable=missing-raises-doc


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
    if isinstance(arg, FunctionType) and isinstance(arg, TypeHintedFunctionType):
        arg_type = arg.output_type()  # built-in function
    elif isinstance(arg, FunctionType):
        return True  # custom-function, can be anything, so pass for now
    elif isinstance(arg, Variable):
        return True  # unresolved variables can be anything, so pass for now

    if is_union(expected_arg_type):
        # See if the arg is a valid against the union
        valid_type = False

        # if the input arg is a union, do a direct comparison
        if is_union(arg_type):
            valid_type = arg_type == expected_arg_type
        # otherwise, iterate the union to see if it's compatible
        else:
            for union_type in expected_arg_type.__args__:
                if issubclass(arg_type, union_type):
                    valid_type = True
                    break

        if not valid_type:
            return False
    # If the input is a union and the expected type is not, see if
    # each possible union input is compatible with the expected type
    elif is_union(arg_type):
        for union_type in arg_type.__args__:
            if not issubclass(union_type, expected_arg_type):
                return False

    elif not issubclass(arg_type, expected_arg_type):
        return False

    return True


@dataclass(frozen=True)
class FunctionInputSpec:
    args: Optional[List[Type[Resolvable | Optional[Resolvable]]]] = None
    varargs: Optional[Type[Resolvable]] = None

    def __post_init__(self):
        assert (self.args is None) ^ (self.varargs is None)

    def _is_args_compatible(self, input_args: List[ArgumentType]) -> bool:
        assert self.args is not None

        if len(input_args) > len(self.args):
            return False

        for idx, arg in enumerate(self.args):
            input_arg = input_args[idx] if idx < len(input_args) else None
            if not is_type_compatible(arg=input_arg, expected_arg_type=arg):
                return False

        return True

    def _is_varargs_compatible(self, input_args: List[ArgumentType]) -> bool:
        assert self.varargs is not None

        for input_arg in input_args:
            if not is_type_compatible(arg=input_arg, expected_arg_type=self.varargs):
                return False

        return True

    def is_compatible(self, input_args: List[ArgumentType]) -> bool:
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
