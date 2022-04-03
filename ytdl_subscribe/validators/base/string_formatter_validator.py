import re
from keyword import iskeyword
from typing import List

from ytdl_subscribe.validators.base.validators import StringValidator


class StringFormatterValidator(StringValidator):
    """
    Ensures user-created formatter strings are valid
    """

    expected_value_type = str
    expected_value_type_name = "format string"

    FIELDS_VALIDATOR = re.compile(r"{([a-z_]+?)}")

    def __validate_and_get_format_variables(self) -> List[str]:
        """
        Returns
        -------
        list[str]
            List of format variables in the format string

        Raises
        -------
        ValidationException
            If the format string contains invalid variable formatting
        """
        open_bracket_count = self.format_string.count("{")
        close_bracket_count = self.format_string.count("}")

        if open_bracket_count != close_bracket_count:
            raise self._validation_exception(
                "Brackets are reserved for {variable_names} and should contain "
                "a single open and close bracket."
            )

        format_variables: List[str] = list(
            re.findall(StringFormatterValidator.FIELDS_VALIDATOR, self.format_string)
        )

        if len(format_variables) != open_bracket_count:
            raise self._validation_exception(
                "{variable_names} should only contain "
                "lowercase letters and underscores with a single open and close bracket."
            )

        for variable in format_variables:
            if iskeyword(variable):
                raise self._validation_exception(
                    f"'{variable}' is a Python keyword and cannot be used as a variable."
                )

        return format_variables

    def __init__(self, name, format_string: str):
        super().__init__(name=name, value=format_string)
        self.format_variables = self.__validate_and_get_format_variables()

    @property
    def format_string(self) -> str:
        """
        Returns
        -------
        The literal format string, unformatted.
        """
        return self._value
