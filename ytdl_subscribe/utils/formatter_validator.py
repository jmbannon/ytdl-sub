import re
from typing import List


class FormatterValidator:
    """
    Ensures user-created formatter strings are valid
    """

    FIELDS_VALIDATOR = re.compile(r"{([a-z_]+?)}")

    def __init__(self, format_string: str):
        self.format_string = format_string
        self._error_prefix = f"Format string '{self.format_string}' is invalid:"

    def parse(self) -> List[str]:
        """
        Returns
        -------
        List of fields to format
        """
        open_bracket_count = self.format_string.count("{")
        close_bracket_count = self.format_string.count("}")

        if open_bracket_count != close_bracket_count:
            raise ValueError(
                f"{self._error_prefix} Brackets are reserved for {{variable_names}} "
                f"and should contain a single open and close bracket."
            )

        parsed_fields = re.findall(
            FormatterValidator.FIELDS_VALIDATOR, self.format_string
        )

        if len(parsed_fields) != open_bracket_count:
            raise ValueError(
                f"{self._error_prefix} {{variable_names}} should only contain "
                f"lowercase letters and underscores with a single open and close bracket."
            )

        return sorted(parsed_fields)
