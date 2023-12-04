import re
from typing import AnyStr
from typing import Match

from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.array import ResolvedArray
from ytdl_sub.script.types.resolvable import String


def _re_output_to_array(re_out: Match[AnyStr] | None) -> ResolvedArray:
    if re_out is None:
        return ResolvedArray([])

    return ResolvedArray(
        list([String(re_out.string)]) + list(String(group) for group in re_out.groups())
    )


class RegexFunctions:
    @staticmethod
    def regex_match(regex: String, string: String) -> Array:
        """
        Cast to String.
        """
        return _re_output_to_array(re.match(regex.value, string.value))

    @staticmethod
    def regex_search(regex: String, string: String) -> Array:
        """
        Cast to String.
        """
        return _re_output_to_array(re.search(regex.value, string.value))

    @staticmethod
    def regex_fullmatch(regex: String, string: String) -> Array:
        return _re_output_to_array(re.fullmatch(regex.value, string.value))
