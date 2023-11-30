from typing import Optional

from ytdl_sub.script.types.map import Map
from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Hashable
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
    def map_contains(mapping: Map, key: Hashable) -> Boolean:
        """
        Returns True if the key is in the Map. False otherwise.
        """
        return Boolean(key in mapping.value)
