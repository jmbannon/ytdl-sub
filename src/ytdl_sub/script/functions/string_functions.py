from typing import Optional

from ytdl_sub.script.types.resolvable import AnyType
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String


class StringFunctions:
    @staticmethod
    def string(value: AnyType) -> String:
        return String(value=str(value.value))

    @staticmethod
    def lower(string: String) -> String:
        """
        Returns
        -------
        Lower-cased string
        """
        return String(string.value.lower())

    @staticmethod
    def upper(string: String) -> String:
        """
        Returns
        -------
        Upper-cased string
        """
        return String(string.value.upper())

    @staticmethod
    def capitalize(string: String) -> String:
        """
        Returns
        -------
        Capitalized string
        """
        return String(string.value.capitalize())

    @staticmethod
    def replace(
        string: String, old: String, new: String, count: Optional[Integer] = None
    ) -> String:
        if count:
            return String(string.value.replace(old.value, new.value, count.value))

        return String(string.value.replace(old.value, new.value))

    @staticmethod
    def concat(*args: String) -> String:
        return String("".join(*args))
