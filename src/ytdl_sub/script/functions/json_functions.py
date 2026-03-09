import json
from typing import Any

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.map import Map
from ytdl_sub.script.types.resolvable import (
    AnyArgument,
    Boolean,
    Float,
    Integer,
    Resolvable,
    String,
)
from ytdl_sub.script.utils.exceptions import UNREACHABLE


def _from_json(out: Any) -> Resolvable:
    # pylint: disable=too-many-return-statements
    if out is None:
        return String("")
    if isinstance(out, int):
        return Integer(out)
    if isinstance(out, float):
        return Float(out)
    if isinstance(out, str):
        return String(out)
    if isinstance(out, bool):
        return Boolean(out)
    if isinstance(out, list):
        return Array(value=[_from_json(arg) for arg in out])
    if isinstance(out, dict):
        return Map(value={_from_json(key): _from_json(value) for key, value in out.items()})
    raise UNREACHABLE


class JsonFunctions:
    @staticmethod
    def from_json(argument: String) -> AnyArgument:
        """
        :description:
          Converts a JSON string into an actual type.
        """
        return _from_json(json.loads(argument.value))
