import math

from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Numeric


def _to_numeric(value: int | float) -> Numeric:
    if int(value) == value:
        return Integer(value=value)
    return Float(value=value)


class NumericFunctions:
    @staticmethod
    def float(value: AnyArgument) -> Float:
        """
        :description:
          Cast to Float.
        """
        return Float(value=float(value.value))

    @staticmethod
    def int(value: AnyArgument) -> Integer:
        """
        :description:
          Cast to Integer.
        """
        return Integer(value=int(value.value))

    @staticmethod
    def add(*values: Numeric) -> Numeric:
        """
        :description:
          ``+`` operator. Returns the sum of all values.
        """
        return _to_numeric(sum(val.value for val in values))

    @staticmethod
    def sub(*values: Numeric) -> Numeric:
        """
        :description:
          ``-`` operator. Subtracts all values from left to right.
        """
        output = values[0].value
        for val in values[1:]:
            output -= val.value

        return _to_numeric(output)

    @staticmethod
    def mul(*values: Numeric) -> Numeric:
        """
        :description:
          ``*`` operator. Returns the product of all values.
        """
        return _to_numeric(math.prod([val.value for val in values]))

    @staticmethod
    def pow(base: Numeric, exponent: Numeric) -> Numeric:
        """
        :description:
          ``**`` operator. Returns the exponential of the base and exponent value.
        """
        return _to_numeric(math.pow(base.value, exponent.value))

    @staticmethod
    def div(left: Numeric, right: Numeric) -> Numeric:
        """
        :description:
          ``/`` operator. Returns ``left / right``.
        """
        return _to_numeric(left.value / right.value)

    @staticmethod
    def mod(left: Numeric, right: Numeric) -> Numeric:
        """
        :description:
          ``%`` operator. Returns ``left % right``.
        """
        return _to_numeric(value=left.value % right.value)

    @staticmethod
    def max(*values: Numeric) -> Numeric:
        """
        :description:
          Returns max of all values.
        """
        return _to_numeric(max(val.value for val in values))

    @staticmethod
    def min(*values: Numeric) -> Numeric:
        """
        :description:
          Returns min of all values.
        """
        return _to_numeric(min(val.value for val in values))
