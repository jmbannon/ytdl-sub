from typing import Callable
from typing import Dict

from ytdl_sub.script.functions.array_functions import ArrayFunctions
from ytdl_sub.script.functions.boolean_functions import BooleanFunctions
from ytdl_sub.script.functions.conditional_functions import ConditionalFunctions
from ytdl_sub.script.functions.date_functions import DateFunctions
from ytdl_sub.script.functions.error_functions import ErrorFunctions
from ytdl_sub.script.functions.map_functions import MapFunctions
from ytdl_sub.script.functions.numeric_functions import NumericFunctions
from ytdl_sub.script.functions.regex_functions import RegexFunctions
from ytdl_sub.script.functions.string_functions import StringFunctions
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.utils.exceptions import FunctionDoesNotExistRuntimeException


class Functions(
    StringFunctions,
    NumericFunctions,
    ConditionalFunctions,
    ArrayFunctions,
    MapFunctions,
    BooleanFunctions,
    ErrorFunctions,
    RegexFunctions,
    DateFunctions,
):
    _custom_functions: Dict[str, Callable[..., Resolvable]] = {}

    @classmethod
    def is_built_in(cls, name: str) -> bool:
        return hasattr(cls, name) or hasattr(cls, f"{name}_") or name in cls._custom_functions

    @classmethod
    def get(cls, name: str) -> Callable[..., Resolvable]:
        if hasattr(cls, name):
            return getattr(cls, name)
        if hasattr(cls, f"{name}_"):
            return getattr(cls, f"{name}_")
        if name in cls._custom_functions:
            return cls._custom_functions[name]

        raise FunctionDoesNotExistRuntimeException(f"The function {name} does not exist")

    @classmethod
    def register_function(cls, function: Callable[..., Resolvable]) -> None:
        if cls.is_built_in(function.__name__):
            raise ValueError(
                f"Cannot register a function with name {function.__name__} because it already exists"
            )
        cls._custom_functions[function.__name__] = function
