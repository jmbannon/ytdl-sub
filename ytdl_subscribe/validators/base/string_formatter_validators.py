import re
from keyword import iskeyword
from typing import Dict
from typing import List
from typing import final

from ytdl_subscribe.validators.base.validators import LiteralDictValidator
from ytdl_subscribe.validators.base.validators import Validator


class StringFormatterValidator(Validator):
    """
    Ensures user-created formatter strings are valid
    """

    _expected_value_type = str
    _expected_value_type_name = "format string"

    __fields_validator = re.compile(r"{([a-z_]+?)}")

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
            re.findall(StringFormatterValidator.__fields_validator, self.format_string)
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

    def __init__(self, name, value: str):
        super().__init__(name=name, value=value)
        self.format_variables = self.__validate_and_get_format_variables()

    @final
    @property
    def format_string(self) -> str:
        """
        Returns
        -------
        The literal format string, unformatted.
        """
        return self._value


class DictFormatterValidator(LiteralDictValidator):
    """
    Validates a dictionary made up of key: string_formatters
    """

    def __init__(self, name, value):
        super().__init__(name, value)

        for key in self._keys:
            self._value[key] = self._validate_key(
                key=key, validator=StringFormatterValidator
            )

    @property
    def dict(self) -> Dict[str, StringFormatterValidator]:
        """Returns dict with string formatter values"""
        return self._value

    @property
    def dict_with_format_strings(self) -> Dict[str, str]:
        """Returns dict with the format strings themselves"""
        return {
            key: string_formatter.format_string
            for key, string_formatter in self.dict.items()
        }
