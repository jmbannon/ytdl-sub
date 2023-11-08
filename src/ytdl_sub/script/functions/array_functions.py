from typing import List

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Resolvable


class ArrayFunctions:
    @staticmethod
    def extend(*arrays: Array) -> Array:
        output: List[Resolvable] = []
        for array in arrays:
            output.extend(array.value)

        return Array(output)

    @staticmethod
    def at(array: Array, idx: Integer) -> Resolvable:
        return array.value[idx.value]

    @staticmethod
    def flatten_array(array: Array) -> Array:
        output: List[Resolvable] = []
        for elem in array.value:
            if isinstance(elem, Array):
                output.extend(ArrayFunctions.flatten_array(elem).value)
            else:
                output.append(elem)

        return Array(output)
