from typing import Optional

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.resolvable import AnyArgument
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import Numeric
from ytdl_sub.script.types.resolvable import String


class StringFunctions:
    @staticmethod
    def string(value: AnyArgument) -> String:
        """
        :description:
          Cast to String.
        """
        return String(value=str(value.value))

    @staticmethod
    def contains(string: String, contains: String) -> Boolean:
        """
        :description:
          Returns True if ``contains`` is in ``string``. False otherwise.
        """
        return Boolean(contains.value in string.value)

    @staticmethod
    def contains_any(string: String, contains_array: Array) -> Boolean:
        """
        :description:
            Returns true if any element in ``contains_array`` is in ``string``. False otherwise.
        """
        return Boolean(
            any(
                str(val) in string.value
                for val in contains_array.value
                if isinstance(val, (String, Integer, Boolean, Float))
            )
        )

    @staticmethod
    def slice(string: String, start: Integer, end: Optional[Integer] = None) -> String:
        """
        :description:
          Returns the slice of the Array.
        """
        if end is not None:
            return String(string.value[start.value : end.value])
        return String(string.value[start.value :])

    @staticmethod
    def lower(string: String) -> String:
        """
        :description:
          Lower-case the entire String.
        """
        return String(string.value.lower())

    @staticmethod
    def upper(string: String) -> String:
        """
        :description:
          Upper-case the entire String.
        """
        return String(string.value.upper())

    @staticmethod
    def capitalize(string: String) -> String:
        """
        :description:
          Capitalize the first character in the string.
        """
        return String(string.value.capitalize())

    @staticmethod
    def titlecase(string: String) -> String:
        """
        :description:
          Capitalize each word in the string.
        """
        return String(string.value.title())

    @staticmethod
    def replace(
        string: String, old: String, new: String, count: Optional[Integer] = None
    ) -> String:
        """
        :description:
          Replace the ``old`` part of the String with the ``new``. Optionally only replace it
          ``count`` number of times.
        """
        if count:
            return String(string.value.replace(old.value, new.value, count.value))

        return String(string.value.replace(old.value, new.value))

    @staticmethod
    def split(string: String, sep: String, max_split: Optional[Integer] = None) -> Array:
        """
        :description:
          Splits the input string into multiple strings.
        """
        if max_split is not None:
            return Array(
                [
                    String(split_val)
                    for split_val in string.value.split(sep=sep.value, maxsplit=max_split.value)
                ]
            )

        return Array([String(split_val) for split_val in string.value.split(sep=sep.value)])

    @staticmethod
    def concat(*values: String) -> String:
        """
        :description:
          Concatenate multiple Strings into a single String.
        """
        return String("".join(val.value for val in values))

    @staticmethod
    def pad(string: String, length: Integer, char: String) -> String:
        """
        :description:
          Pads the string to the given length
        """
        output = string.value
        while len(output) < length.value:
            output = f"{char}{output}"

        return String(output)

    @staticmethod
    def pad_zero(numeric: Numeric, length: Integer) -> String:
        """
        :description:
          Pads a numeric with zeros to the given length
        """
        return StringFunctions.pad(
            string=String(str(numeric.value)),
            length=length,
            char=String("0"),
        )

    @staticmethod
    def unescape(string: String) -> String:
        """
        :description:
          Unescape symbols like newlines or tabs to their true form.

        :usage:

        .. code-block:: python

           {
             %unescape( "Hello\\nWorld" )
           }

           # Hello
           # World
        """
        return String(string.value.encode("utf-8").decode("unicode_escape"))
