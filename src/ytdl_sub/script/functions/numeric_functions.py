from typing import Union

from ytdl_sub.script.types.resolvable import AnyType
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Numeric
from ytdl_sub.script.types.resolvable import String


def _to_numeric(value: int | float) -> Numeric:
    if int(value) == value:
        return Integer(value=value)
    return Float(value=value)


class NumericFunctions:
    @staticmethod
    def float(value: Union[Float, Integer, Boolean, String]) -> Float:
        return Float(value=float(value.value))

    @staticmethod
    def int(value: Union[Float, Integer, Boolean, String]) -> Integer:
        return Integer(value=int(value.value))

    @staticmethod
    def add(left: Numeric, right: Numeric) -> Numeric:
        return _to_numeric(left.value + right.value)

    @staticmethod
    def sub(left: Numeric, right: Numeric) -> Numeric:
        return _to_numeric(left.value - right.value)

    @staticmethod
    def mul(left: Numeric, right: Numeric) -> Numeric:
        return _to_numeric(left.value * right.value)

    @staticmethod
    def div(left: Numeric, right: Numeric) -> Numeric:
        return _to_numeric(left.value / right.value)

    @staticmethod
    def mod(value: Numeric, modulo: Numeric) -> Numeric:
        return _to_numeric(value=value.value % modulo.value)

    @staticmethod
    def max(left: Numeric, right: Numeric) -> Numeric:
        return _to_numeric(max(left.value, right.value))

    @staticmethod
    def min(left: Numeric, right: Numeric) -> Numeric:
        return _to_numeric(min(left.value, right.value))
