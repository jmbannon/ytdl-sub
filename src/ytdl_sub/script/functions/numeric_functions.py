from typing import Union

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
        """
        Cast to Float.
        """
        return Float(value=float(value.value))

    @staticmethod
    def int(value: Union[Float, Integer, Boolean, String]) -> Integer:
        """
        Cast to Integer.
        """
        return Integer(value=int(value.value))

    @staticmethod
    def add(left: Numeric, right: Numeric) -> Numeric:
        """
        ``+`` operator. Returns ``left + right``.
        """
        return _to_numeric(left.value + right.value)

    @staticmethod
    def sub(left: Numeric, right: Numeric) -> Numeric:
        """
        ``-`` operator. Returns ``left - right``.
        """
        return _to_numeric(left.value - right.value)

    @staticmethod
    def mul(left: Numeric, right: Numeric) -> Numeric:
        """
        ``*`` operator. Returns ``left * right``.
        """
        return _to_numeric(left.value * right.value)

    @staticmethod
    def div(left: Numeric, right: Numeric) -> Numeric:
        """
        ``/`` operator. Returns ``left / right``.
        """
        return _to_numeric(left.value / right.value)

    @staticmethod
    def mod(left: Numeric, right: Numeric) -> Numeric:
        """
        ``%`` operator. Returns ``left % right``.
        """
        return _to_numeric(value=left.value % right.value)

    @staticmethod
    def max(*values: Numeric) -> Numeric:
        """
        Returns max of all values.
        """
        return _to_numeric(max(val.value for val in values))

    @staticmethod
    def min(*values: Numeric) -> Numeric:
        """
        Returns min of all values.
        """
        return _to_numeric(min(val.value for val in values))
