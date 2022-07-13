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

    def is_match(self, input_str: str) -> bool:
        """
        Parameters
        ----------
        input_str
            String to match against the regex

        Returns
        -------
        True if input_str matches. False otherwise.
        """
        return self._compiled_regex.search(input_str) is not None

    def capture(self, input_str: str) -> Optional[List[str]]:
        """
        Parameters
        ----------
        input_str
            String to try to regex capture from

        Returns
        -------
        List of captures (will always be >= 1). None if there are no captures.
        """
        if match := self._compiled_regex.search(input_str):
            if len(to_return := list(match.groups())) > 0:
                return to_return
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

    def matches_any(self, input_str: str) -> bool:
        """
        Parameters
        ----------
        input_str
            String to match against any regexes in the list

        Returns
        -------
        True if at least one matches. False if none match
        """
        return any(reg.is_match(input_str) for reg in self._list)

    def capture_any(self, input_str: str) -> Optional[List[str]]:
        """
        Parameters
        ----------
        input_str
            String to try to regex capture from any of the regexes in the list

        Returns
        -------
        List of captures (will always be >= 1) on the first regex that matches. None if
        no regexes match.
        """
        for reg in self._list:
            if maybe_capture := reg.capture(input_str):
                return maybe_capture
        return None
