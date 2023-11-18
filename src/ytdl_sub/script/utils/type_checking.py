from typing import Optional
from typing import Type
from typing import Union
from typing import get_origin

from ytdl_sub.script.types.resolvable import NamedType
from ytdl_sub.script.types.resolvable import Resolvable


def is_union(arg_type: Type) -> bool:
    return get_origin(arg_type) is Union


def is_optional(arg_type: Type) -> bool:
    return is_union(arg_type) and type(None) in arg_type.__args__


def get_optional_type(optional_type: Type) -> Type[NamedType]:
    return [arg for arg in optional_type.__args__ if arg != type(None)][0]


def is_type_compatible(
    arg_type: Type[NamedType],
    expected_arg_type: Type[Resolvable | Optional[Resolvable]],
) -> bool:
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
