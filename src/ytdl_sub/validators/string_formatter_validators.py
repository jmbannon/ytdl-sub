from datetime import datetime
from typing import Any
from typing import Dict
from typing import Set
from typing import Union
from typing import final

from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.script.parser import parse
from ytdl_sub.script.script import Script
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.utils.exceptions import RuntimeException
from ytdl_sub.script.utils.exceptions import ScriptVariableNotResolved
from ytdl_sub.script.utils.exceptions import UserException
from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError
from ytdl_sub.utils.exceptions import StringFormattingVariableNotFoundException
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.validators.validators import DictValidator
from ytdl_sub.validators.validators import ListValidator
from ytdl_sub.validators.validators import LiteralDictValidator
from ytdl_sub.validators.validators import StringValidator
from ytdl_sub.validators.validators import Validator

# pylint: disable=protected-access


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
            self._parsed = parse(
                text=str(value),
                name=self.leaf_name,
            )
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

    @property
    @final
    def parsed(self) -> SyntaxTree:
        """
        Returns
        -------
        The parsed format string.
        """
        return self._parsed

    def post_process(self, resolved: Any) -> Any:
        """
        Returns
        -------
        Apply any post processing to the resolved value. Defaults to casting it to string.
        """
        return str(resolved)


class FloatFormatterValidator(StringFormatterValidator):
    _expected_value_type_name = "float"

    def post_process(self, resolved: str) -> float:
        try:
            out = float(resolved)
        except Exception as exc:
            raise self._validation_exception(
                f"Expected a float, but received '{resolved}'"
            ) from exc

        return out


class StandardizedDateValidator(StringFormatterValidator):
    _expected_value_type_name = "standardized_date"

    def post_process(self, resolved: str) -> str:
        try:
            datetime.strptime(resolved, "%Y-%m-%d")
        except ValueError as exc:
            raise self._validation_exception(
                f"Expected a standardized date in the form of YYYY-MM-DD, but received '{resolved}'"
            ) from exc

        return resolved


class BooleanFormatterValidator(StringFormatterValidator):
    _expected_value_type_name = "boolean"

    def post_process(self, resolved: Any) -> bool:
        return ScriptUtils.bool_formatter_output(output=str(resolved))


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


class OverridesIntegerFormatterValidator(OverridesStringFormatterValidator):
    _expected_value_type_name = "integer"

    def post_process(self, resolved: str) -> int:
        try:
            out = int(resolved)
        except Exception as exc:
            raise self._validation_exception(
                f"Expected an integer, but received '{resolved}'"
            ) from exc
        return out


class OverridesFloatFormatterValidator(FloatFormatterValidator, OverridesStringFormatterValidator):
    """
    Float validator but static
    """


class OverridesBooleanFormatterValidator(
    BooleanFormatterValidator, OverridesStringFormatterValidator
):
    _expected_value_type_name = "boolean"

    def post_process(self, resolved: Any) -> bool:
        return ScriptUtils.bool_formatter_output(output=str(resolved))


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
            # Gets stored in __validator_dict
            _ = self._validate_key(key=key, validator=self._key_validator)

    @property
    def dict(self) -> Dict[str, StringFormatterValidator]:
        """Returns dict with string formatter values"""
        return self._validator_dict

    @property
    def dict_with_format_strings(self) -> Dict[str, str]:
        """Returns dict with the format strings themselves."""
        return {key: string_formatter.format_string for key, string_formatter in self.dict.items()}

    @property
    def dict_with_parsed_format_strings(self) -> Dict[str, SyntaxTree]:
        """Returns dict with the parsed format strings."""
        return {key: string_formatter.parsed for key, string_formatter in self.dict.items()}


class OverridesDictFormatterValidator(DictFormatterValidator):
    """
    A dict made up of
    :class:`~ytdl_sub.validators.string_formatter_validators.OverridesStringFormatterValidator`.
    """

    _key_validator = OverridesStringFormatterValidator


class AnyFormatterValidator(StringFormatterValidator):
    """
    Applies no post-processing.
    """

    def post_process(self, resolved: Any) -> Any:
        return resolved


class AnyOverridesFormatterValidator(AnyFormatterValidator, OverridesStringFormatterValidator):
    pass


class UnstructuredDictFormatterValidator(DictFormatterValidator):
    _key_validator = AnyFormatterValidator

    def __init__(self, name, value):
        # Convert the unstructured-ness into a script
        if isinstance(value, dict):
            value = {key: ScriptUtils.to_native_script(val) for key, val in value.items()}
        super().__init__(name, value)


class UnstructuredOverridesDictFormatterValidator(UnstructuredDictFormatterValidator):
    _key_validator = AnyOverridesFormatterValidator


def _validate_formatter(
    mock_script: Script,
    unresolved_variables: Set[str],
    formatter_validator: Union[StringFormatterValidator, OverridesStringFormatterValidator],
) -> str:
    parsed = formatter_validator.parsed
    if resolved := parsed.maybe_resolvable:
        return resolved.native

    is_static_formatter = isinstance(formatter_validator, OverridesStringFormatterValidator)
    if is_static_formatter:
        unresolved_variables = unresolved_variables.union({VARIABLES.entry_metadata.variable_name})

    variable_names = {var.name for var in parsed.variables}
    custom_function_names = {f"%{func.name}" for func in parsed.custom_functions}

    # Add lambda functions to custom function names, if it's custom
    for lambda_func in parsed.lambdas:
        if lambda_func in mock_script.function_names:
            custom_function_names.add(lambda_func.value)

    if not variable_names.issubset(mock_script.variable_names):
        raise StringFormattingVariableNotFoundException(
            "contains the following variables that do not exist: "
            f"{', '.join(sorted(variable_names - mock_script.variable_names))}"
        )
    if not custom_function_names.issubset(mock_script.function_names):
        raise StringFormattingVariableNotFoundException(
            "contains the following custom functions that do not exist: "
            f"{', '.join(sorted(custom_function_names - mock_script.function_names))}"
        )
    if unresolved := variable_names.intersection(unresolved_variables):
        raise StringFormattingVariableNotFoundException(
            "contains the following variables that are unresolved when executing this "
            f"formatter: {', '.join(sorted(unresolved))}"
        )
    try:
        if is_static_formatter:
            return mock_script.resolve_once_parsed(
                {"tmp_var": formatter_validator.parsed},
                unresolvable=unresolved_variables,
                update=True,
            )["tmp_var"].native

        return formatter_validator.format_string
    except RuntimeException as exc:
        if isinstance(exc, ScriptVariableNotResolved) and is_static_formatter:
            raise StringFormattingVariableNotFoundException(
                "static formatters must contain variables that have no dependency to "
                "entry variables"
            ) from exc
        raise StringFormattingVariableNotFoundException(exc) from exc
    except UserThrownRuntimeError as exc:
        # Errors are expected for non-static formatters due to missing entry
        # data. Raise otherwise.
        if not is_static_formatter:
            return formatter_validator.format_string
        raise exc


def validate_formatters(
    script: Script,
    unresolved_variables: Set[str],
    validator: Validator,
) -> Dict:
    """
    Ensure all OverridesStringFormatterValidator's only contain variables from the overrides
    and resolve.
    """
    resolved_dict: Dict = {}

    if isinstance(validator, DictValidator):
        resolved_dict[validator.leaf_name] = {}
        # Usage of protected variables in other validators is fine. The reason to keep
        # them protected is for readability when using them in subscriptions.
        for validator_value in validator._validator_dict.values():
            resolved_dict[validator.leaf_name] |= validate_formatters(
                script=script,
                unresolved_variables=unresolved_variables,
                validator=validator_value,
            )
    elif isinstance(validator, ListValidator):
        resolved_dict[validator.leaf_name] = []
        for list_value in validator.list:
            list_output = validate_formatters(
                script=script,
                unresolved_variables=unresolved_variables,
                validator=list_value,
            )
            assert len(list_output) == 1
            resolved_dict[validator.leaf_name].append(list(list_output.values())[0])
    elif isinstance(validator, (StringFormatterValidator, OverridesStringFormatterValidator)):
        resolved_dict[validator.leaf_name] = _validate_formatter(
            mock_script=script,
            unresolved_variables=unresolved_variables,
            formatter_validator=validator,
        )
    elif isinstance(validator, (DictFormatterValidator, OverridesDictFormatterValidator)):
        resolved_dict[validator.leaf_name] = {}
        for validator_value in validator.dict.values():
            resolved_dict[validator.leaf_name] |= _validate_formatter(
                mock_script=script,
                unresolved_variables=unresolved_variables,
                formatter_validator=validator_value,
            )
    else:
        resolved_dict[validator.leaf_name] = validator._value

    return resolved_dict
