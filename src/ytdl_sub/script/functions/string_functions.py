from typing import Optional

from ytdl_sub.script.types.resolvable import AnyType
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String


class StringFunctions:
    @staticmethod
    def string(value: AnyType) -> String:
        """
        Cast to String.
        """
        return String(value=str(value.value))

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
        Capitalize all words in the String.
        """
        return String(string.value.capitalize())

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
    def concat(*args: String) -> String:
        """
        Concatenate multiple Strings into a single String.
        """
        return String("".join(*args))
