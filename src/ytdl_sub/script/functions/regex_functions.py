import re
from typing import AnyStr
from typing import Match

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String


def _re_output_to_array(re_out: Match[AnyStr] | None) -> Array:
    if re_out is None:
        return Array([])

    return Array(list([String(re_out.string)]) + list(String(group) for group in re_out.groups()))


class RegexFunctions:
    @staticmethod
    def regex_match(regex: String, string: String) -> Array:
        """
        :description:
          Checks for a match only at the beginning of the string. If a match exists, returns
          the string as the first element of the Array. If there are capture groups, returns each
          group as a subsequent element in the Array.
        """
        return _re_output_to_array(re.match(regex.value, string.value))

    @staticmethod
    def regex_search(regex: String, string: String) -> Array:
        """
        :description:
          Checks for a match anywhere in the string. If a match exists, returns
          the string as the first element of the Array. If there are capture groups, returns each
          group as a subsequent element in the Array.
        """
        return _re_output_to_array(re.search(regex.value, string.value))

    @staticmethod
    def regex_fullmatch(regex: String, string: String) -> Array:
        """
        :description:
          Checks for entire string to be a match. If a match exists, returns
          the string as the first element of the Array. If there are capture groups, returns each
          group as a subsequent element in the Array.
        """
        return _re_output_to_array(re.fullmatch(regex.value, string.value))

    @staticmethod
    def regex_capture_groups(regex: String) -> Integer:
        """
        :description:
          Returns number of capture groups in regex
        """
        return Integer(re.compile(regex.value).groups)

    @staticmethod
    def regex_sub(regex: String, replacement: String, string: String) -> String:
        """
        :description:
          Returns the string obtained by replacing the leftmost non-overlapping occurrences of the
          pattern in string by the replacement string. The replacement string can reference the
          match groups via backslash escapes. Callables as replacement argument are not supported.
        """
        return String(re.sub(regex.value, replacement.value, string.value))
