import re
from typing import List
from typing import Optional

from ytdl_sub.validators.validators import ListValidator
from ytdl_sub.validators.validators import StringValidator


class RegexValidator(StringValidator):
    _expected_value_type_name = "regex"

    def __init__(self, name, value):
        super().__init__(name, value)

        try:
            self._compiled_regex = re.compile(self.value)
        except Exception as exc:
            raise self._validation_exception(
                error_message=f"invalid regex: '{self.value}'"
            ) from exc

    @property
    def num_capture_groups(self) -> int:
        """
        Returns
        -------
        Number of capture groups in the regex
        """
        return self._compiled_regex.groups

    @property
    def compiled_regex(self) -> re.Pattern:
        """
        Returns
        -------
        The regex compiled
        """
        return self._compiled_regex

    def match(self, input_str: str) -> Optional[List[str]]:
        """
        Parameters
        ----------
        input_str
            String to regex match

        Returns
        -------
        List of captures. If the regex has no capture groups, then the list will be emtpy.
        None is returned if the input_str failed to match
        """
        if match := self._compiled_regex.search(input_str):
            return list(match.groups())
        return None


class RegexListValidator(ListValidator[RegexValidator]):
    _expected_value_type_name = "regex list"
    _inner_list_type = RegexValidator

    def __init__(self, name, value):
        super().__init__(name, value)

        if len(set(reg.num_capture_groups for reg in self._list)) > 1:
            raise self._validation_exception(
                "each regex in a list must have the same number of capture groups"
            )

        self._num_capture_groups = self._list[0].num_capture_groups

    @property
    def num_capture_groups(self) -> int:
        """
        Returns
        -------
        Number of capture groups. All regexes in the list will have the same number.
        """
        return self._num_capture_groups

    def match_any(self, input_str: str) -> Optional[List[str]]:
        """
        Parameters
        ----------
        input_str
            String to try to regex capture from any of the regexes in the list

        Returns
        -------
        List of captures on the first regex that matches. If the regex has no capture groups, then
        the list will be emtpy. None is returned if the input_str failed to match
        """
        for reg in self._list:
            if (maybe_capture := reg.match(input_str)) is not None:
                return maybe_capture
        return None
