from typing import Optional

from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Numeric
from ytdl_sub.script.types.resolvable import String


class StringFunctions:
    @staticmethod
    def string(value: AnyArgument) -> String:
        """
        Cast to String.
        """
        return String(value=str(value.value))

    @staticmethod
    def contains(string: String, contains: String) -> Boolean:
        """
        Returns True if ``contains`` is in ``string``. False otherwise.
        """
        return Boolean(contains.value in string.value)

    @staticmethod
    def slice(string: String, start: Integer, end: Optional[Integer] = None) -> String:
        """
        Returns the slice of the Array.
        """
        if end is not None:
            return String(string.value[start.value : end.value])
        return String(string.value[start.value :])

    @staticmethod
    def lower(string: String) -> String:
        """
        Lower-case the entire String.
        """
        return String(string.value.lower())

    @staticmethod
    def upper(string: String) -> String:
        """
        Upper-case the entire String.
        """
        return String(string.value.upper())

    @staticmethod
    def capitalize(string: String) -> String:
        """
        Capitalize the first character in the string.
        """
        return String(string.value.capitalize())

    @staticmethod
    def titlecase(string: String) -> String:
        """
        Capitalize each word in the string.
        """
        return String(string.value.title())

    @staticmethod
    def replace(
        string: String, old: String, new: String, count: Optional[Integer] = None
    ) -> String:
        """
        Replace the ``old`` part of the String with the ``new``. Optionally only replace it
        ``count`` number of times.
        """
        if count:
            return String(string.value.replace(old.value, new.value, count.value))

        return String(string.value.replace(old.value, new.value))

    @staticmethod
    def concat(*values: String) -> String:
        """
        Concatenate multiple Strings into a single String.
        """
        return String("".join(val.value for val in values))

    @staticmethod
    def pad(string: String, length: Integer, char: String) -> String:
        """
        Pads the string to the given length
        """
        output = string.value
        while len(output) < length.value:
            output = f"{char}{output}"

        return String(output)

    @staticmethod
    def pad_zero(numeric: Numeric, length: Integer) -> String:
        """
        Pads a numeric with zeros to the given length
        """
        return StringFunctions.pad(
            string=String(str(numeric.value)),
            length=length,
            char=String("0"),
        )
