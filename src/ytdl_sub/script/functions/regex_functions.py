import re
from typing import AnyStr
from typing import List
from typing import Match
from typing import Optional

from ytdl_sub.script.functions.array_functions import ArrayFunctions
from ytdl_sub.script.types.array import Array
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Float
from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.utils.exceptions import FunctionRuntimeException


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
    def regex_search_any(string: String, regex_array: Array) -> Boolean:
        """
        :description:
          Returns True if any regex pattern in the regex array matches the string. False otherwise.
        """
        return Boolean(
            any(
                len(RegexFunctions.regex_search(regex=String(str(regex)), string=string).value) > 0
                for regex in regex_array.value
                if isinstance(regex, (String, Integer, Boolean, Float))
            )
        )

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

    @staticmethod
    def regex_capture_many(
        string: String, regex_array: Array, default: Optional[Array] = None
    ) -> Array:
        """
        :description:
          Returns the input string and first regex's capture groups that match to the string
          in an array. If a default is not provided, then all number of regex capture groups
          must be equal across all regex strings. In addition, an error will be thrown if
          no matches are found.

          If the default is provided, then the number of capture groups must be less than
          or equal to the length of the default value array. Any element not captured
          will return the respective default value.
        :usage:

        .. code-block:: python

           {
             %regex_capture_many(
               "2020-02-27",
               [
                 "No (.*) matches here",
                 "([0-9]+)-([0-9]+)-27"
               ],
               [ "01", "01" ]
             )
           }

           # ["2020-02-27", "2020", "02"]
        """
        if len(regex_array) == 0:
            raise FunctionRuntimeException("regex_array must contain at least a single element")

        regex_list: List[String] = []
        for regex in regex_array.value:
            if not isinstance(regex, String):
                raise FunctionRuntimeException("All regex_array elements must be strings")
            regex_list.append(regex)

        if default is None:
            num_capture_groups = RegexFunctions.regex_capture_groups(regex_list[0]).value
            if any(
                RegexFunctions.regex_capture_groups(regex).value != num_capture_groups
                for regex in regex_list[1:]
            ):
                raise FunctionRuntimeException(
                    "regex_array elements must contain the same number of capture groups"
                )
        elif any(
            RegexFunctions.regex_capture_groups(regex).value > len(default) for regex in regex_list
        ):
            raise FunctionRuntimeException(
                "When using %regex_capture_array, number of regex capture groups must be less than "
                "or equal to the number of defaults"
            )

        output = Array([])
        for regex in regex_list:
            output = RegexFunctions.regex_search(regex=regex, string=string)
            if len(output) > 0:
                break

        if len(output) == 0 and not default:
            raise FunctionRuntimeException(
                f"no regex strings were captured for input string {string.value}"
            )

        if default is not None:
            default_output = Array([string] + default.value)
            return ArrayFunctions.array_overlay(output, default_output, only_missing=Boolean(True))

        return output

    @staticmethod
    def regex_capture_many_with_defaults(
        string: String, regex_array: Array, default: Optional[Array]
    ) -> Array:
        """
        :description:
          Deprecated. Use %regex_capture_many instead.
        """
        return RegexFunctions.regex_capture_many(string, regex_array, default)

    @staticmethod
    def regex_capture_many_required(string: String, regex_array: Array) -> Array:
        """
        :description:
          Deprecated. Use %regex_capture_many instead.
        """
        return RegexFunctions.regex_capture_many(string, regex_array)
