from ytdl_sub.script.functions.array_functions import ArrayFunctions
from ytdl_sub.script.functions.boolean_functions import BooleanFunctions
from ytdl_sub.script.functions.conditional_functions import ConditionalFunctions
from ytdl_sub.script.functions.error_functions import ErrorFunctions
from ytdl_sub.script.functions.map_functions import MapFunctions
from ytdl_sub.script.functions.numeric_functions import NumericFunctions
from ytdl_sub.script.functions.string_functions import StringFunctions


class Functions(
    StringFunctions,
    NumericFunctions,
    ConditionalFunctions,
    ArrayFunctions,
    MapFunctions,
    BooleanFunctions,
    ErrorFunctions,
):
    @classmethod
    def is_built_in(cls, name: str) -> bool:
        return hasattr(cls, name) or hasattr(cls, name + "_")
