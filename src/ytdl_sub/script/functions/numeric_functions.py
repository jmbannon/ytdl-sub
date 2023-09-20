from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Numeric


def _to_numeric(value: int | float) -> Numeric:
    if int(value) == value:
        return Integer(value=value)
    return Float(value=value)


class NumericFunctions:
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
    def mod(value: Integer, modulo: Integer) -> Integer:
        return Integer(value=value.value % modulo.value)
