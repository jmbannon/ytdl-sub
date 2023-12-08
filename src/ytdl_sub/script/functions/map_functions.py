from typing import Optional

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.map import Map
from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Hashable
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import LambdaThree
from ytdl_sub.script.types.resolvable import LambdaTwo
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import KeyDoesNotExistRuntimeException


class MapFunctions:
    @staticmethod
    def map_get(mapping: Map, key: Hashable, default: Optional[AnyArgument] = None) -> AnyArgument:
        """
        Return ``key``'s value within the Map. If ``key`` does not exist, and ``default`` is
        provided, it will return ``default``. Otherwise, will error.
        """
        if key not in mapping.value:
            if default is not None:
                return default

            raise KeyDoesNotExistRuntimeException(
                f"Tried to call %map_get with key {key.value}, but it does not exist"
            )
        return mapping.value[key]

    @staticmethod
    def map_get_non_empty(mapping: Map, key: Hashable, default: AnyArgument) -> AnyArgument:
        """
        Return ``key``'s value within the Map. If ``key`` does not exist or is an empty string,
        return ``default``. Otherwise, will error.
        """
        output = MapFunctions.map_get(mapping, key, default)
        if isinstance(output, String) and output.value == "":
            return default
        return output

    @staticmethod
    def map_contains(mapping: Map, key: Hashable) -> Boolean:
        """
        Returns True if the key is in the Map. False otherwise.
        """
        return Boolean(key in mapping.value)

    # pylint: disable=unused-argument

    @staticmethod
    def map_apply(mapping: Map, lambda_function: LambdaTwo) -> Array:
        """
        Apply a lambda function on the Map, where each arg
        passed to the lambda function is ``key, value`` as two separate args.
        """
        return Array([Array([key, value]) for key, value in mapping.value.items()])

    @staticmethod
    def map_enumerate(mapping: Map, lambda_function: LambdaThree) -> Array:
        """
        Apply a lambda function on the Map, where each arg
        passed to the lambda function is ``idx, key, value`` as three separate args.
        """
        return Array(
            [
                Array([Integer(idx), key_value[0], key_value[1]])
                for idx, key_value in enumerate(mapping.value.items())
            ]
        )
