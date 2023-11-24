from typing import List

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Lambda
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

        return ResolvedArray(output)

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

        return ResolvedArray(output)

    @staticmethod
    def array_reverse(array: Array) -> Array:
        """
        Reverse an Array.
        """
        return ResolvedArray(list(reversed(array.value)))

    # pylint: disable=unused-argument

    @staticmethod
    def array_apply(array: Array, lambda_function: Lambda) -> Array:
        """
        Apply a lambda function on every element in the Array.
        """
        return ResolvedArray([ResolvedArray([val]) for val in array.value])

    @staticmethod
    def array_enumerate(array: Array, lambda_function: Lambda) -> Array:
        """
        Apply a lambda function on every element in the Array, where each arg
        passed to the lambda function is ``idx, element`` as two separate args.
        """
        return ResolvedArray(
            [ResolvedArray([Integer(idx), val]) for idx, val in enumerate(array.value)]
        )

    # pylint: enable=unused-argument
