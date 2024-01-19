import itertools
from typing import List
from typing import Optional

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Lambda
from ytdl_sub.script.types.resolvable import LambdaReduce
from ytdl_sub.script.types.resolvable import LambdaTwo
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.utils.exceptions import UNREACHABLE
from ytdl_sub.script.utils.exceptions import ArrayValueDoesNotExist
from ytdl_sub.script.utils.exceptions import FunctionRuntimeException


class ArrayFunctions:
    @staticmethod
    def array(maybe_array: AnyArgument) -> Array:
        """
        :description:
          Tries to cast an unknown variable type to an Array.
        """
        if not isinstance(maybe_array, Array):
            raise FunctionRuntimeException(
                f"Tried and failed to cast {maybe_array.type_name()} as an Array"
            )
        return maybe_array

    @staticmethod
    def array_size(array: Array) -> Integer:
        """
        :description:
          Returns the size of an Array.
        """
        return Integer(len(array.value))

    @staticmethod
    def array_extend(*arrays: Array) -> Array:
        """
        :description:
          Combine multiple Arrays into a single Array.
        """
        output: List[Resolvable] = []
        for array in arrays:
            output.extend(array.value)

        return Array(output)

    @staticmethod
    def array_overlay(
        array: Array, overlap: Array, only_missing: Optional[Boolean] = None
    ) -> Array:
        """
        :description:
          Overlaps ``overlap`` onto ``array``. Can optionally only overlay missing indices.
        """
        output: List[Resolvable] = []
        output.extend(array.value)

        overlap_only_missing = only_missing and only_missing.value

        for idx, overlap_value in enumerate(overlap.value):
            if overlap_only_missing and idx < len(array.value):
                continue

            if idx < len(array.value):
                output[idx] = overlap_value
            else:
                output.append(overlap_value)

        return Array(output)

    @staticmethod
    def array_at(array: Array, idx: Integer, default: Optional[AnyArgument] = None) -> AnyArgument:
        """
        :description:
          Return the element in the Array at index ``idx``. If ``idx`` exceeds the array length,
          either return ``default`` if provided or throw an error.
        """
        try:
            return array.value[idx.value]
        except IndexError:
            if default is not None:
                return default
            raise

    @staticmethod
    def array_first(array: Array, fallback: AnyArgument) -> AnyArgument:
        """
        :description:
          Returns the first element whose boolean conversion is True. Returns fallback
          if all elements evaluate to False.
        """
        for val in array.value:
            if bool(val.value):
                return val

        return fallback

    @staticmethod
    def array_contains(array: Array, value: AnyArgument) -> Boolean:
        """
        :description:
          Return True if the value exists in the Array. False otherwise.
        """
        return Boolean(value in array.value)

    @staticmethod
    def array_index(array: Array, value: AnyArgument) -> Integer:
        """
        :description:
          Return the index of the value within the Array if it exists. If it does not, it will
          throw an error.
        """
        if not ArrayFunctions.array_contains(array=array, value=value):
            raise ArrayValueDoesNotExist(
                "Tried to get the index of a value in an Array that does not exist"
            )

        if isinstance(value, Resolvable):
            return Integer(array.value.index(value))

        raise UNREACHABLE

    @staticmethod
    def array_slice(array: Array, start: Integer, end: Optional[Integer] = None) -> Array:
        """
        :description:
          Returns the slice of the Array.
        """
        if end is not None:
            return Array(array.value[start.value : end.value])
        return Array(array.value[start.value :])

    @staticmethod
    def array_flatten(array: Array) -> Array:
        """
        :description:
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
        :description:
          Reverse an Array.
        """
        return Array(list(reversed(array.value)))

    @staticmethod
    def array_product(*arrays: Array) -> Array:
        """
        :description:
          Returns the Cartesian product of elements from different arrays
        """
        out: List[Resolvable] = []
        for combo in itertools.product(*[arr.value for arr in arrays]):
            out.append(Array(combo))

        return Array(out)

    # pylint: disable=unused-argument

    @staticmethod
    def array_apply(array: Array, lambda_function: Lambda) -> Array:
        """
        :description:
          Apply a lambda function on every element in the Array.
        :usage:

        .. code-block:: python

           {
             %array_apply( [1, 2, 3] , %string )
           }

           # ["1", "2", "3"]
        """
        return Array([Array([val]) for val in array.value])

    @staticmethod
    def array_apply_fixed(
        array: Array,
        fixed_argument: AnyArgument,
        lambda2_function: LambdaTwo,
        reverse_args: Optional[Boolean] = None,
    ) -> Array:
        """
        :description:
          Apply a lambda function on every element in the Array, with ``fixed_argument``
          passed as a second argument to every invocation.
        """
        if reverse_args and reverse_args.value:
            return Array([Array([fixed_argument, val]) for val in array.value])

        return Array([Array([val, fixed_argument]) for val in array.value])

    @staticmethod
    def array_enumerate(array: Array, lambda_function: LambdaTwo) -> Array:
        """
        :description:
          Apply a lambda function on every element in the Array, where each arg
          passed to the lambda function is ``idx, element`` as two separate args.
        """
        return Array([Array([Integer(idx), val]) for idx, val in enumerate(array.value)])

    @staticmethod
    def array_reduce(array: Array, lambda_reduce_function: LambdaReduce) -> AnyArgument:
        """
        :description:
          Apply a reduce function on pairs of elements in the Array, until one element remains.
          Executes using the left-most and reduces in the right direction.
        """
        return array
