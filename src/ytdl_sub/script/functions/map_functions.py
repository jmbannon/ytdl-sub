from typing import Dict
from typing import List

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.resolvable import Map
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.utils.exceptions import StringFormattingException


class MapFunctions:
    @staticmethod
    def map(*key_values: Array) -> Map:
        output: Dict[Resolvable, Resolvable] = {}

        for key_value in key_values:
            if len(key_value.value) != 2:
                raise StringFormattingException(
                    "%map must take Arrays containing pairs of keys and values"
                )

            output[key_value.value[0]] = key_value.value[1]

        return Map(output)
