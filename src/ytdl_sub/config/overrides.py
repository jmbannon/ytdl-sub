from typing import Any
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Set
from typing import Type
from typing import TypeVar

from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.variables.override_variables import REQUIRED_OVERRIDE_VARIABLE_NAMES
from ytdl_sub.entries.variables.override_variables import OverrideHelpers
from ytdl_sub.script.parser import parse
from ytdl_sub.script.script import Script
from ytdl_sub.script.types.function import BuiltInFunction
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import String
from ytdl_sub.script.types.syntax_tree import SyntaxTree
from ytdl_sub.script.utils.exceptions import ScriptVariableNotResolved
from ytdl_sub.utils.exceptions import InvalidVariableNameException
from ytdl_sub.utils.exceptions import StringFormattingException
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.utils.scriptable import Scriptable
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import UnstructuredDictFormatterValidator

ExpectedT = TypeVar("ExpectedT")


class Overrides(UnstructuredDictFormatterValidator, Scriptable):
    """
    Allows you to define variables that can be used in any EntryFormatter or OverridesFormatter.

    :Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           overrides:
             output_directory: "/path/to/media"
             custom_file_name: "{upload_date_standardized}.{title_sanitized}"

           # Then use the override variables in the output options
           output_options:
             output_directory: "{output_directory}"
             file_name: "{custom_file_name}.{ext}"
             thumbnail_name: "{custom_file_name}.{thumbnail_ext}"

    Override variables can contain explicit values and other variables, including both override
    and source variables.

    In addition, any override variable defined will automatically create a ``sanitized`` variable
    for use. In the example above, ``output_directory_sanitized`` will exist and perform
    sanitization on the value when used.
    """

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        dict_formatter = UnstructuredDictFormatterValidator(name=name, value=value)
        _ = [parse(format_string) for format_string in dict_formatter.dict_with_format_strings]

    def __init__(self, name, value):
        UnstructuredDictFormatterValidator.__init__(self, name, value)
        Scriptable.__init__(self, initialize_base_script=True)

        for key in self._keys:
            self.ensure_variable_name_valid(key)

        self.unresolvable.add(VARIABLES.entry_metadata.variable_name)
        self.unresolvable.update(REQUIRED_OVERRIDE_VARIABLE_NAMES)

    def ensure_added_plugin_variable_valid(self, added_variable: str) -> bool:
        """
        Returns False if the variable exists as a non-override.

        Raises
        ------
        ValidationException
            If the variable is already added as an override variable.
        """
        try:
            self.ensure_variable_name_valid(added_variable)
        except ValidationException:
            return False

        if added_variable in self.keys:
            raise self._validation_exception(
                f"Override variable with name {added_variable} cannot be used since it is"
                " added by a plugin."
            )

        return True

    def ensure_variable_names_not_a_plugin(self, plugin_names: Iterable[str]) -> None:
        """
        Throws an error if an override variable or function has the same name as a
        preset key. This is to avoid confusion when accidentally defining things in
        overrides that are meant to be in the preset.
        """
        for name in self.keys:
            if name.startswith("%"):
                name = name[1:]

            if name in plugin_names:
                raise self._validation_exception(
                    f"Override variable with name {name} cannot be used since it is"
                    " the name of a plugin. Perhaps you meant to define it as a plugin? If so,"
                    " indent it left to make it at the same level as overrides.",
                    exception_class=InvalidVariableNameException,
                )

    def ensure_variable_name_valid(self, name: str) -> None:
        """
        Ensures the variable name does not collide with any entry variables or built-in functions.
        """
        if not OverrideHelpers.is_valid_name(name):
            override_type = "function" if name.startswith("%") else "variable"
            raise self._validation_exception(
                f"Override {override_type} with name {name} is invalid. Names must be"
                " lower_snake_cased and begin with a letter.",
                exception_class=InvalidVariableNameException,
            )

        if OverrideHelpers.is_entry_variable_name(name):
            raise self._validation_exception(
                f"Override variable with name {name} cannot be used since it is a"
                " built-in ytdl-sub entry variable name.",
                exception_class=InvalidVariableNameException,
            )

        if OverrideHelpers.is_function_name(name):
            raise self._validation_exception(
                f"Override function definition with name {name} cannot be used since it is"
                " a built-in ytdl-sub function name.",
                exception_class=InvalidVariableNameException,
            )

    def initial_variables(
        self, unresolved_variables: Optional[Dict[str, SyntaxTree]] = None
    ) -> Dict[str, SyntaxTree]:
        """
        Returns
        -------
        Variables and format strings for all Override variables + additional variables (Optional)
        """
        initial_variables: Dict[str, SyntaxTree] = self.dict_with_parsed_format_strings
        if unresolved_variables:
            initial_variables |= unresolved_variables
        return ScriptUtils.add_sanitized_parsed_variables(initial_variables)

    def initialize_script(self, unresolved_variables: Set[str]) -> "Overrides":
        """
        Initialize the override script with any unresolved variables
        """
        self.script.add_parsed(
            self.initial_variables(
                unresolved_variables={
                    var_name: SyntaxTree(
                        ast=[
                            BuiltInFunction(
                                name="throw",
                                args=[
                                    String(f"Plugin variable {var_name} has not been created yet")
                                ],
                            )
                        ]
                    )
                    for var_name in unresolved_variables
                }
            )
        )
        self.unresolvable.update(unresolved_variables)
        self.update_script()
        return self

    def _apply_to_resolvable(
        self,
        formatter: StringFormatterValidator,
        entry: Optional[Entry],
        function_overrides: Optional[Dict[str, str]],
    ) -> Resolvable:
        script: Script = self.script
        unresolvable: Set[str] = self.unresolvable
        if entry:
            script = entry.script
            unresolvable = entry.unresolvable

        # Update the script internally so long as we are not supplying overrides
        # that could alter the script with one-off state
        update = function_overrides is None

        try:
            return script.resolve_once(
                dict({"tmp_var": formatter.format_string}, **(function_overrides or {})),
                unresolvable=unresolvable,
                update=update,
            )["tmp_var"]
        except ScriptVariableNotResolved as exc:
            raise StringFormattingException(
                "Tried to resolve the following script, but could not due to unresolved "
                f"variables:\n {formatter.format_string}\n"
                "This is most likely due to circular dependencies in variables. "
                "If you think otherwise, please file a bug on GitHub and post your config. Thanks!"
            ) from exc

    def apply_formatter(
        self,
        formatter: StringFormatterValidator,
        entry: Optional[Entry] = None,
        function_overrides: Optional[Dict[str, str]] = None,
        expected_type: Type[ExpectedT] = str,
    ) -> ExpectedT:
        """
        Parameters
        ----------
        formatter
            Formatter to apply
        entry
            Optional. Entry to add source variables to the formatter
        function_overrides
            Optional. Explicit values to override the overrides themselves and source variables
        expected_type
            The expected type that should return. Defaults to string.

        Returns
        -------
        The format_string after .format has been called

        Raises
        ------
        StringFormattingException
            If the formatter that is trying to be resolved cannot
        """
        out = formatter.post_process(
            self._apply_to_resolvable(
                formatter=formatter, entry=entry, function_overrides=function_overrides
            ).native
        )

        if not isinstance(out, expected_type):
            raise StringFormattingException(
                f"Expected type {expected_type.__name__}, but received '{out.__class__.__name__}'"
            )

        return out
