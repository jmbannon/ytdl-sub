from typing import List

from ytdl_sub.script.types.resolvable import Array
from ytdl_sub.script.types.resolvable import Resolvable


class ArrayFunctions:
    @staticmethod
    def extend(*arrays: Array) -> Array:
        output: List[Resolvable] = []
        for array in arrays:
            output.extend(array.value)

        return Array(output)
