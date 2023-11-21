from typing import Optional

from ytdl_sub.script.types.map import Map
from ytdl_sub.script.types.resolvable import AnyType
from ytdl_sub.script.types.resolvable import Hashable


class MapFunctions:
    @staticmethod
    def map_get(mapping: Map, key: Hashable, default: Optional[AnyType] = None) -> AnyType:
        """
        Return ``key``'s value within the Map. If ``key`` does not exist, and ``default`` is
        provided, it will return ``default``. Otherwise, will error.
        """
        if default is not None:
            return mapping.value.get(key, default=default)
        return mapping.value[key]
