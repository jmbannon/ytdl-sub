from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.exceptions import RegexNoMatchException
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.regex_validator import RegexListValidator
from ytdl_sub.validators.source_variable_validator import SourceVariableNameListValidator
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import ListFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import BoolValidator

logger = Logger.get(name="regex")


class SourceVariableRegex(StrictDictValidator):

    _required_keys = {"match"}
    _optional_keys = {"defaults", "capture_group_names"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._match = self._validate_key(key="match", validator=RegexListValidator)
        self._defaults = self._validate_key_if_present(
            key="defaults", validator=ListFormatterValidator
        )
        self._capture_group_names = self._validate_key_if_present(
            key="capture_group_names", validator=SourceVariableNameListValidator, default=[]
        )

        # If defaults are to be used, ensure there are the same number of defaults as there are
        # capture groups
        if self._defaults is not None and self._match.num_capture_groups != len(
            self._defaults.list
        ):
            raise self._validation_exception(
                f"number of defaults must match number of capture groups, "
                f"{len(self._defaults.list)} != {self._match.num_capture_groups}"
            )

        # If there are capture groups, ensure there are capture group names
        if len(self._capture_group_names.list) != self._match.num_capture_groups:
            raise self._validation_exception(
                f"Number of capture group names must match number of capture groups, "
                f"{len(self._capture_group_names.list)} != {self._match.num_capture_groups}"
            )

    @property
    def capture_list(self) -> RegexListValidator:
        """
        Returns
        -------
        List of regex captures
        """
        return self._match

    @property
    def has_defaults(self) -> bool:
        """
        Returns
        -------
        True if a validation exception should be raised if not captured. False otherwise.
        """
        return self._defaults is not None

    @property
    def defaults(self) -> Optional[List[StringFormatterValidator]]:
        """
        Returns
        -------
        List of string format validators to use for the defaults
        """
        return self._defaults.list if self.has_defaults else None

    @property
    def capture_group_names(self) -> List[str]:
        """
        Returns
        -------
        List of new capture group names
        """
        return [validator.value for validator in self._capture_group_names.list]


class FromSourceVariablesRegex(StrictDictValidator):

    _optional_keys = Entry.source_variables()
    _allow_extra_keys = True

    def __init__(self, name, value):
        super().__init__(name, value)
        self.source_variable_capture_dict: Dict[str, SourceVariableRegex] = {
            key: self._validate_key(key=key, validator=SourceVariableRegex) for key in self._keys
        }


class RegexOptions(PluginOptions):
    r"""
    Performs regex matching on an entry's source variables. Regex can be used to filter entries
    from proceeding with download or capture groups to create new source variables.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           regex:
             # By default, if any match fails and has no defaults, the entry will be skipped.
             # If set to False, ytdl-sub will error and stop all downloads from proceeding.
             skip_if_match_fails: True

             from:
               title:
                 # Match with capture groups act as a filter.
                 # This will only download videos with "Official Video" in it.
                 match: "\[Official Video\]"
               description:
                 # Match with capture groups and defaults.
                 # This tries to scrape a date from the description and produce new source variables
                 match: "([0-9]{4})-([0-9]{2})-([0-9]{2})"

                 # Each capture group creates these new source variables, respectively
                 capture_group_names:
                  - "captured_upload_year"
                  - "captured_upload_month"
                  - "captured_upload_day"

                 # And if the string does not match, use these as respective default values for the
                 # new source variables.
                 capture_group_defaults:
                   - "{upload_year}"
                   - "{upload_month}"
                   - "{upload_day}"
    """

    _required_keys = {"from"}
    _optional_keys = {"skip_if_match_fails"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._from = self._validate_key(key="from", validator=FromSourceVariablesRegex)
        self.skip_if_match_fails: bool = self._validate_key_if_present(
            key="skip_if_match_fails", validator=BoolValidator, default=False
        ).value

    def validate_with_source_variables(self, source_variables: List[str]) -> None:
        """
        Ensures each source variable capture group is valid

        Parameters
        ----------
        source_variables
            Variables to check against the provided capture groups
        """
        for key in self.source_variable_capture_dict.keys():
            if key not in source_variables:
                raise self._validation_exception(
                    f"cannot regex capture '{key}' because it is not a source variable"
                )

    @property
    def source_variable_capture_dict(self) -> Dict[str, SourceVariableRegex]:
        """
        Returns
        -------
        Dict of { source variable: capture options }
        """
        return self._from.source_variable_capture_dict

    def added_source_variables(self) -> List[str]:
        """
        Returns
        -------
        List of new source variables created via regex capture
        """
        added_source_vars: List[str] = []
        for regex_options in self.source_variable_capture_dict.values():
            added_source_vars.extend(regex_options.capture_group_names)

        return added_source_vars


class RegexPlugin(Plugin[RegexOptions]):
    plugin_options_type = RegexOptions

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        """
        Parameters
        ----------
        entry
            Entry to add source variables to

        Returns
        -------
        Entry with regex capture variables added to its source variables

        Raises
        ------
        ValidationException
            If no capture and no defaults
        """
        entry_variable_dict = entry.to_dict()

        # Iterate each source var to capture and add to the entry
        for source_var, regex_options in self.plugin_options.source_variable_capture_dict.items():
            maybe_capture = regex_options.capture_list.match_any(
                input_str=entry_variable_dict[source_var]
            )

            # If no capture
            if maybe_capture is None:
                # and no defaults
                if not regex_options.has_defaults:
                    # Skip the entry if toggled
                    if self.plugin_options.skip_if_match_fails:
                        logger.info(
                            "Regex failed to match '%s' from '%s', skipping.",
                            source_var,
                            entry.title,
                        )
                        return None

                    # Otherwise, error
                    raise RegexNoMatchException(
                        f"Regex failed to match '{source_var}' from '{entry.title}'"
                    )

                # otherwise, use defaults (apply them using the original entry source dict)
                source_variables_and_overrides_dict = dict(
                    entry_variable_dict, **self.overrides.dict_with_format_strings
                )
                entry.add_variables(
                    variables_to_add={
                        regex_options.capture_group_names[i]: default.apply_formatter(
                            variable_dict=source_variables_and_overrides_dict
                        )
                        for i, default in enumerate(regex_options.defaults)
                    },
                )
            # There is a capture, add the source variables to the entry as
            # {source_var}_capture_1, {source_var}_capture_2, ...
            else:
                entry.add_variables(
                    variables_to_add={
                        regex_options.capture_group_names[i]: capture
                        for i, capture in enumerate(maybe_capture)
                    },
                )

        return entry
