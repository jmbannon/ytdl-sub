import re
from typing import AnyStr
from typing import Match

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.resolvable import String


def _re_output_to_array(re_out: Match[AnyStr] | None) -> Array:
    if re_out is None:
        return Array([])

    return Array(list([String(re_out.string)]) + list(String(group) for group in re_out.groups()))


class RegexFunctions:
    @staticmethod
    def regex_match(regex: String, string: String) -> Array:
        """
        Checks for a match only at the beginning of the string. If a match exists, returns
        the string as the first element of the Array. If there are capture groups, returns each
        group as a subsequent element in the Array.
        """
        return _re_output_to_array(re.match(regex.value, string.value))

    @staticmethod
    def regex_search(regex: String, string: String) -> Array:
        """
        Checks for a match anywhere in the string. If a match exists, returns
        the string as the first element of the Array. If there are capture groups, returns each
        group as a subsequent element in the Array.
        """
        return _re_output_to_array(re.search(regex.value, string.value))

    @staticmethod
    def regex_fullmatch(regex: String, string: String) -> Array:
        """
        Checks for entire string to be a match. If a match exists, returns
        the string as the first element of the Array. If there are capture groups, returns each
        group as a subsequent element in the Array.
        """
        return _re_output_to_array(re.fullmatch(regex.value, string.value))
