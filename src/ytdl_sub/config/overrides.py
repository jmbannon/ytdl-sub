import copy
from typing import Any
from typing import Dict
from typing import Set
from typing import Type
from typing import TypeVar
from typing import final

from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import Variable
from ytdl_sub.entries.script.variable_scripts import UNRESOLVED_VARIABLES
from ytdl_sub.entries.script.variable_scripts import VARIABLE_SCRIPTS
from ytdl_sub.entries.variables.override_variables import SUBSCRIPTION_NAME
from ytdl_sub.script.parser import parse
from ytdl_sub.script.script import Script
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator

TType = TypeVar("TType")


class Overrides(DictFormatterValidator):
    """
    Optional. This section allows you to define variables that can be used in any string formatter.
    For example, if you want your file and thumbnail files to match without copy-pasting a large
    format string, you can define something like:

    .. code-block:: yaml

       presets:
         my_example_preset:
           overrides:
             output_directory: "/path/to/media"
             custom_file_name: "{upload_year}.{upload_month_padded}.{upload_day_padded}.{title_sanitized}"

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
        dict_formatter = DictFormatterValidator(name=name, value=value)
        _ = [parse(format_string) for format_string in dict_formatter.dict_with_format_strings]

    # pylint: enable=line-too-long

    def _add_override_variable(self, key_name: str, format_string: str, sanitize: bool = False):
        if sanitize:
            key_name = f"{key_name}_sanitized"
            format_string = sanitize_filename(format_string)

        self._value[key_name] = StringFormatterValidator(
            name="__should_never_fail__",
            value=format_string,
        )

    def __init__(self, name, value):
        super().__init__(name, value)

        # Add sanitized overrides
        for key in self._keys:
            self._add_override_variable(
                key_name=key,
                format_string=self._value[key].format_string,
                sanitize=True,
            )

        if SUBSCRIPTION_NAME not in self._value:
            for sanitized in [True, False]:
                self._add_override_variable(
                    key_name=SUBSCRIPTION_NAME,
                    format_string=self.subscription_name,
                    sanitize=sanitized,
                )

        self.script = Script(copy.deepcopy(VARIABLE_SCRIPTS))
        self.unresolvable: Set[str] = copy.deepcopy(UNRESOLVED_VARIABLES)

    def initialize_script(self, unresolved_variables: Set[str]) -> None:
        self.unresolvable |= unresolved_variables
        self.script.add(
            dict(
                self.dict_with_format_strings,
                **{
                    unresolved: f"{{%throw('Variable {unresolved} has not been resolved yet')}}"
                    for unresolved in self.unresolvable
                },
            )
        )
        self.update_script()

    def add_entry_kwargs(self, entry_kwargs: Dict[str, Any]) -> "Overrides":
        self.unresolvable.remove(VARIABLES.entry_metadata.variable_name)
        self.script.add(
            {VARIABLES.entry_metadata.variable_name: ScriptUtils.to_script(entry_kwargs)}
        )
        self.update_script()
        return self

    def add(self, values: Dict[str, Any]) -> None:
        self.unresolvable -= set(list(values.keys()))
        self.script.add(
            ScriptUtils.add_sanitized_variables(
                {name: ScriptUtils.to_script(value) for name, value in values.items()}
            ),
            unresolvable=self.unresolvable,
        )
        self.update_script()

    def update_script(self) -> None:
        self.script.resolve(unresolvable=self.unresolvable, update=True)

    def get(self, variable: Variable | str, expected_type: Type[TType]) -> TType:
        out = self.script.resolve(unresolvable=self.unresolvable).get_native(variable.variable_name)
        return expected_type(out)

    def get_str(self, variable: Variable) -> str:
        return self.get(variable, str)

    def get_int(self, variable: Variable) -> int:
        return self.get(variable, int)

    @property
    def subscription_name(self) -> str:
        """
        Returns
        -------
        Name of the subscription
        """
        return self._root_name

    @final
    def to_dict(self) -> Dict[str, str]:
        """
        Returns
        -------
        Dictionary containing all variables
        """
        return self.script.resolve().as_native()

    def apply_formatter(
        self,
        formatter: StringFormatterValidator,
        function_overrides: Dict[str, str] = None,
    ) -> str:
        """
        Parameters
        ----------
        formatter
            Formatter to apply
        entry
            Optional. Entry to add source variables to the formatter
        function_overrides
            Optional. Explicit values to override the overrides themselves and source variables

        Returns
        -------
        The format_string after .format has been called
        """
        return formatter.post_process(
            str(
                self.script.resolve_once(
                    dict({"tmp_var": formatter.format_string}, **(function_overrides or {})),
                    unresolvable=self.unresolvable.union(
                        VARIABLES.entry_metadata.variable_name
                        if isinstance(formatter, OverridesStringFormatterValidator)
                        else set()
                    ),
                )["tmp_var"]
            )
        )
