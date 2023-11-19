from ytdl_sub.script.types.resolvable import AnyType
from ytdl_sub.script.types.resolvable import Boolean


class BooleanFunctions:
    """
    Comparison functions that output Booleans.
    """

    @staticmethod
    def bool(value: AnyType) -> Boolean:
        """
        Cast any type to a Boolean.
        """
        return Boolean(bool(value.value))

    @staticmethod
    def eq(left: AnyType, right: AnyType) -> Boolean:
        """
        ``==`` operator. Returns True if left == right. False otherwise.
        """
        return Boolean(left.value == right.value)

    @staticmethod
    def ne(left: AnyType, right: AnyType) -> Boolean:
        """
        ``!=`` operator. Returns True if left != right. False otherwise.
        """
        return Boolean(left.value != right.value)

    @staticmethod
    def lt(left: AnyType, right: AnyType) -> Boolean:
        """
        ``<`` operator. Returns True if left < right. False otherwise.
        """
        return Boolean(left.value < right.value)

    @staticmethod
    def lte(left: AnyType, right: AnyType) -> Boolean:
        """
        ``<=`` operator. Returns True if left <= right. False otherwise.
        """
        return Boolean(left.value <= right.value)

    @staticmethod
    def gt(left: AnyType, right: AnyType) -> Boolean:
        """
        ``>`` operator. Returns True if left > right. False otherwise.
        """
        return Boolean(left.value > right.value)

    @staticmethod
    def gte(left: AnyType, right: AnyType) -> Boolean:
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
