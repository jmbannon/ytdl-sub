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
    String that can use
    :class:`source variables <ytdl_sub.entries.variables.entry_variables.SourceVariables>`
    and
    :class:`overrides <ytdl_sub.config.preset_options.Overrides>`
    for populating things like file paths and metadata.

    .. code-block:: python

       "{tv_show_file_name}.s{upload_year}.e{upload_month}{upload_day_padded}.{ext}"

    is valid when using
    :class:`youtube variables <ytdl_sub.entries.variables.youtube_variables.YoutubeVideoVariables>`
    with the following overrides:

    .. code-block:: yaml

       presets:
         my_example_preset:
           overrides:
             tv_show_file_name: "sweet_tv_show"

    and would resolve to something like ``sweet_tv_show.s2022.e502.mp4``.
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
        ------
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
        """
        Calls `format` on the format string using the variable_dict as input kwargs

        Parameters
        ----------
        variable_dict
            kwargs to pass to the format string

        Returns
        -------
        Format string formatted
        """
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


# pylint: disable=line-too-long
class OverridesStringFormatterValidator(StringFormatterValidator):
    """
    String that can `only` use :class:`overrides <ytdl_sub.config.preset_options.Overrides>`.

    Used in fields that do not touch the downloaded files themselves, but instead, `single`
    things like
    :func:`output_directory <ytdl_sub.config.preset_options.OutputOptions.output_directory>`
    or the fields in
    :class:`nfo_output_directory <ytdl_sub.plugins.output_directory_nfo_tags.OutputDirectoryNfoTagsOptions>`
    """


# pylint: enable=line-too-long


class DictFormatterValidator(LiteralDictValidator):
    """
    A dict made up of
    :class:`~ytdl_sub.validators.string_formatter_validators.StringFormatterValidator`.
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
    A dict made up of
    :class:`~ytdl_sub.validators.string_formatter_validators.OverridesStringFormatterValidator`.
    """

    _key_validator = OverridesStringFormatterValidator
