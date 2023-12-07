import copy
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set

from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.variables.override_variables import SUBSCRIPTION_NAME
from ytdl_sub.script.parser import parse
from ytdl_sub.utils.scriptable import Scriptable
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator


class Overrides(DictFormatterValidator, Scriptable):
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
        DictFormatterValidator.__init__(self, name, value)
        Scriptable.__init__(self)

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

        self.unresolvable.add(VARIABLES.entry_metadata.variable_name)

    def initialize_script(self, unresolved_variables: Dict[str, str]) -> None:
        self.script.add(dict(self.dict_with_format_strings, **unresolved_variables))
        self.unresolvable.update(set(unresolved_variables.keys()))

        self.update_script()

    @property
    def subscription_name(self) -> str:
        """
        Returns
        -------
        Name of the subscription
        """
        return self._root_name

    def apply_formatter(
        self,
        formatter: StringFormatterValidator,
        entry: Optional[Entry] = None,
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
        if entry:
            script = copy.deepcopy(entry.script)
            unresolvable = entry.unresolvable
        else:
            script = copy.deepcopy(self.script)
            unresolvable = self.unresolvable

        if function_overrides:
            script.add(function_overrides)

        return (
            script.add({"tmp_var": formatter.format_string})
            .resolve(unresolvable=unresolvable)
            .get_str("tmp_var")
        )
