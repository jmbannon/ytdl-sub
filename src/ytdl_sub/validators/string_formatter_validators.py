from typing import Dict
from typing import Set
from typing import Union
from typing import final

from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.script.parser import parse
from ytdl_sub.script.script import Script
from ytdl_sub.script.utils.exceptions import UserException
from ytdl_sub.script.utils.exceptions import VariableDoesNotExist
from ytdl_sub.utils.exceptions import StringFormattingVariableNotFoundException
from ytdl_sub.validators.validators import DictValidator
from ytdl_sub.validators.validators import ListValidator
from ytdl_sub.validators.validators import LiteralDictValidator
from ytdl_sub.validators.validators import StringValidator
from ytdl_sub.validators.validators import Validator


class StringFormatterValidator(StringValidator):
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

    _expected_value_type_name = "format string"

    def __init__(self, name, value: str):
        super().__init__(name=name, value=value)
        try:
            _ = parse(str(value))
        except UserException as exc:
            raise self._validation_exception(exc) from exc

    @property
    @final
    def format_string(self) -> str:
        """
        Returns
        -------
        The literal format string, unformatted.
        """
        return self._value

    # pylint: disable=no-self-use

    def post_process(self, resolved: str) -> str:
        """
        Returns
        -------
        Apply any post processing to the resolved value
        """
        return resolved

    # pylint: enable=no-self-use


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


class OverridesIntegerFormatterValidator(StringFormatterValidator):
    _expected_value_type_name = "integer"

    def post_process(self, resolved: str) -> str:
        try:
            int(resolved)
        except Exception as exc:
            raise self._validation_exception(
                f"Expected an integer, but received '{resolved}'"
            ) from exc

        return resolved


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


def _validate_formatter(
    mock_script: Script,
    unresolved_variables: Set[str],
    formatter_validator: Union[StringFormatterValidator, OverridesStringFormatterValidator],
) -> None:
    try:
        unresolvable = unresolved_variables
        if isinstance(formatter_validator, OverridesStringFormatterValidator):
            unresolvable = unresolved_variables.union({VARIABLES.entry_metadata.variable_name})

        mock_script.resolve_once(
            {"tmp_var": formatter_validator.format_string},
            unresolvable=unresolvable,
        )
    except VariableDoesNotExist as exc:
        raise StringFormattingVariableNotFoundException(exc) from exc


def validate_formatters(
    script: Script,
    unresolved_variables: Set[str],
    validator: Validator,
) -> None:
    """
    Ensure all OverridesStringFormatterValidator's only contain variables from the overrides
    and resolve.
    """
    if isinstance(validator, DictValidator):
        # pylint: disable=protected-access
        # Usage of protected variables in other validators is fine. The reason to keep
        # them protected is for readability when using them in subscriptions.
        for validator_value in validator._validator_dict.values():
            validate_formatters(
                script=script,
                unresolved_variables=unresolved_variables,
                validator=validator_value,
            )
        # pylint: enable=protected-access
    elif isinstance(validator, ListValidator):
        for list_value in validator.list:
            validate_formatters(
                script=script,
                unresolved_variables=unresolved_variables,
                validator=list_value,
            )
    elif isinstance(validator, (StringFormatterValidator, OverridesStringFormatterValidator)):
        _validate_formatter(
            mock_script=script,
            unresolved_variables=unresolved_variables,
            formatter_validator=validator,
        )
    elif isinstance(validator, (DictFormatterValidator, OverridesDictFormatterValidator)):
        for validator_value in validator.dict.values():
            _validate_formatter(
                mock_script=script,
                unresolved_variables=unresolved_variables,
                formatter_validator=validator_value,
            )
