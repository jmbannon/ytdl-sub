from typing import Optional

from ytdl_sub.script.functions.conditional_functions import ConditionalFunctions
from ytdl_sub.script.functions.numeric_functions import NumericFunctions
from ytdl_sub.script.functions.string_functions import StringFunctions


class Functions(StringFunctions, NumericFunctions, ConditionalFunctions):
    pass
