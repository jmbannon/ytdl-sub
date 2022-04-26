import re
from collections import OrderedDict
from keyword import iskeyword
from typing import Dict
from typing import List
from typing import final

from ytdl_sub.utils.exceptions import StringFormattingException
from ytdl_sub.utils.exceptions import StringFormattingVariableNotFoundException
from ytdl_sub.validators.validators import LiteralDictValidator
from ytdl_sub.validators.validators import Validator


class StringFormatterValidator(Validator):
    """
    Ensures user-created formatter strings are valid
    """

    _expected_value_type = str
    _expected_value_type_name = "format string"

    __fields_validator = re.compile(r"{([a-z_]+?)}")

    __max_format_recursion = 3

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
                "a single open and close bracket.",
                exception_class=StringFormattingException,
            )

        format_variables: List[str] = list(
            re.findall(StringFormatterValidator.__fields_validator, self.format_string)
        )

        if len(format_variables) != open_bracket_count:
            raise self._validation_exception(
                "{variable_names} should only contain "
                "lowercase letters and underscores with a single open and close bracket.",
                exception_class=StringFormattingException,
            )

        for variable in format_variables:
            if iskeyword(variable):
                raise self._validation_exception(
                    f"'{variable}' is a Python keyword and cannot be used as a variable.",
                    exception_class=StringFormattingException,
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

    def __apply_formatter(
        self, formatter: "StringFormatterValidator", variable_dict: Dict[str, str]
    ) -> "StringFormatterValidator":
        """TODO: test recursive case where variable not found"""
        # Ensure the variable names exist within the entry and overrides
        for variable_name in formatter.format_variables:
            if variable_name not in variable_dict:
                available_fields = ", ".join(sorted(variable_dict.keys()))
                raise self._validation_exception(
                    f"Format variable '{variable_name}' does not exist. "
                    f"Available variables: {available_fields}",
                    exception_class=StringFormattingVariableNotFoundException,
                )

        return StringFormatterValidator(
            name=self._name,
            value=formatter.format_string.format(**OrderedDict(variable_dict)),
        )

    @final
    def apply_formatter(self, variable_dict: Dict[str, str]) -> str:
        # Keep formatting the format string until no format_variables are present
        formatter = self
        recursion_depth = 0
        max_depth = StringFormatterValidator.__max_format_recursion

        while formatter.format_variables and recursion_depth < max_depth:
            formatter = self.__apply_formatter(formatter=formatter, variable_dict=variable_dict)
            recursion_depth += 1

        if formatter.format_variables:
            raise self._validation_exception(
                f"Attempted to format but failed after reaching max recursion depth of "
                f"{max_depth}. Try to keep variables dependent on only one other variable at max. "
                f"Unresolved variables: {', '.join(sorted(formatter.format_variables))}",
                exception_class=StringFormattingException,
            )

        return formatter.format_string


class OverridesStringFormatterValidator(StringFormatterValidator):
    """
    A string formatter that should strictly use overrides that resolve without any entry variables.
    """


class DictFormatterValidator(LiteralDictValidator):
    """
    Validates a dictionary made up of key: string_formatters
    """

    _key_validator = StringFormatterValidator

    def __init__(self, name, value):
        super().__init__(name, value)

        for key in self._keys:
            self._value[key] = self._validate_key(key=key, validator=self._key_validator)

    @property
    def dict(self) -> Dict[str, StringFormatterValidator]:
        """Returns dict with string formatter values"""
        return self._value

    @property
    def dict_with_format_strings(self) -> Dict[str, str]:
        """Returns dict with the format strings themselves"""
        return {key: string_formatter.format_string for key, string_formatter in self.dict.items()}


class OverridesDictFormatterValidator(DictFormatterValidator):
    """
    Validates a dictionary made up of key: string_formatters, that must be resolved by overrides
    only.
    """

    _key_validator = OverridesStringFormatterValidator
