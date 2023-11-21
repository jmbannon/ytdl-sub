from typing import List

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Resolvable


class ArrayFunctions:
    @staticmethod
    def array_extend(*arrays: Array) -> Array:
        """
        Combine multiple Arrays into a single Array.
        """
        output: List[Resolvable] = []
        for array in arrays:
            output.extend(array.value)

        return Array(output)

    @staticmethod
    def array_at(array: Array, idx: Integer) -> Resolvable:
        """
        Return the element in the Array at index ``idx``.
        """
        return array.value[idx.value]

    @staticmethod
    def array_flatten(array: Array) -> Array:
        """
        Flatten any nested Arrays into a single-dimensional Array.
        """
        output: List[Resolvable] = []
        for elem in array.value:
            if isinstance(elem, Array):
                output.extend(ArrayFunctions.array_flatten(elem).value)
            else:
                output.append(elem)

        return Array(output)

    @staticmethod
    def array_reverse(array: Array) -> Array:
        """
        Reverse an Array.
        """
        return Array(list(reversed(array.value)))
