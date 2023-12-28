from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import String

# pylint: disable=invalid-name


class BooleanFunctions:
    """
    Comparison functions that output Booleans.
    """

    @staticmethod
    def bool(value: AnyArgument) -> Boolean:
        """
        :description:
          Cast any type to a Boolean.
        """
        return Boolean(bool(value.value))

    @staticmethod
    def eq(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        :description:
          ``==`` operator. Returns True if left == right. False otherwise.
        """
        return Boolean(left.value == right.value)

    @staticmethod
    def ne(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        :description:
          ``!=`` operator. Returns True if left != right. False otherwise.
        """
        return Boolean(left.value != right.value)

    @staticmethod
    def lt(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        :description:
          ``<`` operator. Returns True if left < right. False otherwise.
        """
        return Boolean(left.value < right.value)

    @staticmethod
    def lte(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        :description:
          ``<=`` operator. Returns True if left <= right. False otherwise.
        """
        return Boolean(left.value <= right.value)

    @staticmethod
    def gt(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        :description:
          ``>`` operator. Returns True if left > right. False otherwise.
        """
        return Boolean(left.value > right.value)

    @staticmethod
    def gte(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        :description:
          ``>=`` operator. Returns True if left >= right. False otherwise.
        """
        return Boolean(left.value >= right.value)

    @staticmethod
    def and_(*values: AnyArgument) -> Boolean:
        """
        :description:
          ``and`` operator. Returns True if all values evaluate to True. False otherwise.
        """
        return Boolean(all(bool(val.value) for val in values))

    @staticmethod
    def or_(*values: AnyArgument) -> Boolean:
        """
        :description:
          ``or`` operator. Returns True if any value evaluates to True. False otherwise.
        """
        return Boolean(any(bool(val.value) for val in values))

    @staticmethod
    def xor(*values: AnyArgument) -> Boolean:
        """
        :description:
          ``^`` operator. Returns True if exactly one value is set to True. False otherwise.
        """
        bit_array = [bool(val.value) for val in values]

        return Boolean(sum(bit_array) == 1)

    @staticmethod
    def not_(value: Boolean) -> Boolean:
        """
        :description:
          ``not`` operator. Returns the opposite of value.
        """
        return Boolean(not value.value)

    @staticmethod
    def is_null(value: AnyArgument) -> Boolean:
        """
        :description:
          Returns True if a value is null (i.e. an empty string). False otherwise.
        """
        return Boolean(isinstance(value, String) and value.value == "")
