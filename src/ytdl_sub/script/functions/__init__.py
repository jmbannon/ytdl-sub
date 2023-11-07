from typing import Optional

from ytdl_sub.script.functions.array_functions import ArrayFunctions
from ytdl_sub.script.functions.map_functions import MapFunctions
from ytdl_sub.script.functions.numeric_functions import NumericFunctions
from ytdl_sub.script.functions.special_functions import SpecialFunctions
from ytdl_sub.script.functions.string_functions import StringFunctions


class Functions(StringFunctions, NumericFunctions, SpecialFunctions, ArrayFunctions, MapFunctions):
    pass
