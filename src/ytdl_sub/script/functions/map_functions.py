from typing import Dict
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
from ytdl_sub.script.utils.exceptions import FunctionRuntimeException
from ytdl_sub.script.utils.exceptions import KeyDoesNotExistRuntimeException
from ytdl_sub.script.utils.exceptions import KeyNotHashableRuntimeException


class MapFunctions:
    @staticmethod
    def map(maybe_mapping: AnyArgument) -> Map:
        """
        :description:
          Tries to cast an unknown variable type to a Map.
        """
        if not isinstance(maybe_mapping, Map):
            raise FunctionRuntimeException(
                f"Tried and failed to cast {maybe_mapping.type_name()} as a Map"
            )
        return maybe_mapping

    @staticmethod
    def map_size(mapping: Map) -> Integer:
        """
        :description:
          Returns the size of a Map.
        """
        return Integer(len(mapping.value))

    @staticmethod
    def map_contains(mapping: Map, key: AnyArgument) -> Boolean:
        """
        :description:
          Returns True if the key is in the Map. False otherwise.
        """
        if not isinstance(key, Hashable):
            raise KeyNotHashableRuntimeException(
                f"Tried to use {key.type_name()} as a Map key, but it is not hashable."
            )

        return Boolean(key in mapping.value)

    @staticmethod
    def map_get(
        mapping: Map, key: AnyArgument, default: Optional[AnyArgument] = None
    ) -> AnyArgument:
        """
        :description:
          Return ``key``'s value within the Map. If ``key`` does not exist, and ``default`` is
          provided, it will return ``default``. Otherwise, will error.
        """
        if not MapFunctions.map_contains(mapping=mapping, key=key).value:
            if default is not None:
                return default

            raise KeyDoesNotExistRuntimeException(
                f"Tried to call %map_get with key {key.value}, but it does not exist"
            )
        return mapping.value[key]

    @staticmethod
    def map_extend(*maps: Map) -> Map:
        """
        :description:
          Return maps combined in the order from left-to-right. Duplicate keys will use the
          right-most map's value.
        """
        output_dict: Dict = {}
        for map_i in maps:
            output_dict |= map_i.value

        return Map(output_dict)

    @staticmethod
    def map_get_non_empty(mapping: Map, key: AnyArgument, default: AnyArgument) -> AnyArgument:
        """
        :description:
          Return ``key``'s value within the Map. If ``key`` does not exist or is an empty string,
          return ``default``. Otherwise, will error.
        """
        output = MapFunctions.map_get(mapping, key, default)
        if isinstance(output, String) and output.value == "":
            return default
        return output

    # pylint: disable=unused-argument

    @staticmethod
    def map_apply(mapping: Map, lambda_function: LambdaTwo) -> Array:
        """
        :description:
          Apply a lambda function on the Map, where each arg
          passed to the lambda function is ``key, value`` as two separate args.
        """
        return Array([Array([key, value]) for key, value in mapping.value.items()])

    @staticmethod
    def map_enumerate(mapping: Map, lambda_function: LambdaThree) -> Array:
        """
        :description:
          Apply a lambda function on the Map, where each arg
          passed to the lambda function is ``idx, key, value`` as three separate args.
        """
        return Array(
            [
                Array([Integer(idx), key_value[0], key_value[1]])
                for idx, key_value in enumerate(mapping.value.items())
            ]
        )
