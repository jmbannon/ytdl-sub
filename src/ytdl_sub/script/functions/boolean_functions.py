from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Boolean

# pylint: disable=invalid-name


class BooleanFunctions:
    """
    Comparison functions that output Booleans.
    """

    @staticmethod
    def bool(value: AnyArgument) -> Boolean:
        """
        Cast any type to a Boolean.
        """
        return Boolean(bool(value.value))

    @staticmethod
    def eq(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        ``==`` operator. Returns True if left == right. False otherwise.
        """
        return Boolean(left.value == right.value)

    @staticmethod
    def ne(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        ``!=`` operator. Returns True if left != right. False otherwise.
        """
        return Boolean(left.value != right.value)

    @staticmethod
    def lt(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        ``<`` operator. Returns True if left < right. False otherwise.
        """
        return Boolean(left.value < right.value)

    @staticmethod
    def lte(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        ``<=`` operator. Returns True if left <= right. False otherwise.
        """
        return Boolean(left.value <= right.value)

    @staticmethod
    def gt(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        ``>`` operator. Returns True if left > right. False otherwise.
        """
        return Boolean(left.value > right.value)

    @staticmethod
    def gte(left: AnyArgument, right: AnyArgument) -> Boolean:
        """
        ``>=`` operator. Returns True if left >= right. False otherwise.
        """
        return Boolean(left.value >= right.value)

    @staticmethod
    def and_(left: Boolean, right: Boolean) -> Boolean:
        """
        ``and`` operator. Returns True if left and right are both True. False otherwise.
        """
        return Boolean(left.value and right.value)

    @staticmethod
    def or_(left: Boolean, right: Boolean) -> Boolean:
        """
        ``or`` operator. Returns True if either left or right are True. False otherwise.
        """
        return Boolean(left.value or right.value)

    @staticmethod
    def xor(left: Boolean, right: Boolean) -> Boolean:
        """
        ``^`` operator. Returns True if either left or right are True and the other is False.
        Returns False otherwise.
        """
        return Boolean(left.value ^ right.value)

    @staticmethod
    def not_(value: Boolean) -> Boolean:
        """
        ``not`` operator. Returns the opposite of value.
        """
        return Boolean(not value.value)
