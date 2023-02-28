import re
from collections import OrderedDict
from keyword import iskeyword
from typing import Dict
from typing import List
from typing import final

from yt_dlp.utils import sanitize_filename

from ytdl_sub.utils.exceptions import InvalidVariableNameException
from ytdl_sub.utils.exceptions import StringFormattingException
from ytdl_sub.utils.exceptions import StringFormattingVariableNotFoundException
from ytdl_sub.validators.validators import ListValidator
from ytdl_sub.validators.validators import LiteralDictValidator
from ytdl_sub.validators.validators import Validator

_fields_validator = re.compile(r"{([a-z][a-z0-9_]+?)}")

_fields_validator_exception_message: str = (
    "{variable_names} must start with a lowercase letter, should only contain lowercase letters, "
    "numbers, underscores, and have a single open and close bracket."
)


def is_valid_source_variable_name(input_str: str, raise_exception: bool = False) -> bool:
    """
    Parameters
    ----------
    input_str
        String to see if it can be a source variable
    raise_exception
        Raise InvalidVariableNameException False.

    Returns
    -------
    True if it is. False otherwise.

    Raises
    ------
    InvalidVariableNameException
        If raise_exception and output is False
    """
    # Add brackets around it to pretend its a StringFormatter, see if it captures
    is_source_variable_name = len(re.findall(_fields_validator, f"{{{input_str}}}")) > 0
    if not is_source_variable_name and raise_exception:
        raise InvalidVariableNameException(_fields_validator_exception_message)
    return is_source_variable_name


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
    _variable_not_found_error_msg_formatter = (
        "Format variable '{variable_name}' does not exist. Available variables: {available_fields}"
    )

    _max_format_recursion = 8

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

        format_variables: List[str] = list(re.findall(_fields_validator, self.format_string))

        if len(format_variables) != open_bracket_count:
            raise self._validation_exception(
                error_message=_fields_validator_exception_message,
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

    def _apply_formatter(
        self, formatter: "StringFormatterValidator", variable_dict: Dict[str, str]
    ) -> "StringFormatterValidator":
        # Ensure the variable names exist within the entry and overrides
        for variable_name in formatter.format_variables:
            # If the variable exists, but is sanitized...
            if (
                variable_name.endswith("_sanitized")
                and variable_name.removesuffix("_sanitized") in variable_dict
            ):
                # Resolve just the non-sanitized version, then sanitize it
                variable_dict[variable_name] = sanitize_filename(
                    StringFormatterValidator(
                        name=self._name, value=f"{{{variable_name.removesuffix('_sanitized')}}}"
                    ).apply_formatter(variable_dict)
                )
            # If the variable doesn't exist, error
            elif variable_name not in variable_dict:
                available_fields = ", ".join(sorted(variable_dict.keys()))
                raise self._validation_exception(
                    self._variable_not_found_error_msg_formatter.format(
                        variable_name=variable_name, available_fields=available_fields
                    ),
                    exception_class=StringFormattingVariableNotFoundException,
                )

        return StringFormatterValidator(
            name=self._name,
            value=formatter.format_string.format(**OrderedDict(variable_dict)),
        )

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
        formatter = self
        recursion_depth = 0
        max_depth = self._max_format_recursion

        while formatter.format_variables and recursion_depth < max_depth:
            formatter = self._apply_formatter(formatter=formatter, variable_dict=variable_dict)
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

    _variable_not_found_error_msg_formatter = (
        "Override variable '{variable_name}' does not exist. For this field, ensure your override "
        "variable does not contain any source variables - it is a requirement that this be a "
        "static string. Available override variables: {available_fields}"
    )


# pylint: enable=line-too-long


class ListFormatterValidator(ListValidator[StringFormatterValidator]):
    _inner_list_type = StringFormatterValidator


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
