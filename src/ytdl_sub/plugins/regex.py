from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from yt_dlp.utils import sanitize_filename

from ytdl_sub.config.plugin import Plugin
from ytdl_sub.config.plugin import PluginPriority
from ytdl_sub.config.preset_options import OptionsDictValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.kwargs import YTDL_SUB_REGEX_SOURCE_VARS
from ytdl_sub.utils.exceptions import RegexNoMatchException
from ytdl_sub.utils.exceptions import StringFormattingVariableNotFoundException
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.regex_validator import RegexListValidator
from ytdl_sub.validators.source_variable_validator import SourceVariableNameListValidator
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import ListFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import BoolValidator

logger = Logger.get(name="regex")


class VariableRegex(StrictDictValidator):

    _optional_keys = {"match", "exclude", "capture_group_defaults", "capture_group_names"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._match = self._validate_key_if_present(key="match", validator=RegexListValidator)
        self._exclude = self._validate_key_if_present(key="exclude", validator=RegexListValidator)
        self._capture_group_defaults = self._validate_key_if_present(
            key="capture_group_defaults", validator=ListFormatterValidator
        )
        self._capture_group_names = self._validate_key_if_present(
            key="capture_group_names", validator=SourceVariableNameListValidator, default=[]
        )

        if self._match is None and self._exclude is None:
            raise self._validation_exception("must specify either `match` or `exclude`")

        if self._match is None and (self._capture_group_defaults or self._capture_group_names.list):
            raise self._validation_exception(
                "capture group parameters requires at least one `match` to be specified"
            )

        # If defaults are to be used, ensure there are the same number of defaults as there are
        # capture groups
        if self._capture_group_defaults is not None and self._match.num_capture_groups != len(
            self._capture_group_defaults.list
        ):
            raise self._validation_exception(
                f"number of defaults must match number of capture groups, "
                f"{len(self._capture_group_defaults.list)} != {self._match.num_capture_groups}"
            )

        # If there are capture groups, ensure there are capture group names
        if self._match and (len(self._capture_group_names.list) != self._match.num_capture_groups):
            raise self._validation_exception(
                f"number of capture group names must match number of capture groups, "
                f"{len(self._capture_group_names.list)} != {self._match.num_capture_groups}"
            )

    @property
    def match(self) -> Optional[RegexListValidator]:
        """
        List of regex strings to try to match against a source or override variable. Each regex
        string must have the same number of capture groups.
        """
        return self._match

    @property
    def exclude(self) -> Optional[RegexListValidator]:
        """
        List of regex strings to try to match against a source or override variable. If one of the
        regex strings match, then the entry will be skipped. If both ``exclude`` and ``match`` are
        specified, entries will get skipped if the regex matches against both ``exclude`` and
        ``match``.
        """
        return self._exclude

    @property
    def capture_group_names(self) -> Optional[List[str]]:
        """
        Optional (only when no capture groups are in the regex string). List of names to store the
        capture group values to. These and ``_sanitized`` versions will be available to use as
        source variables. The list's length must be equal to the number of match capture groups.
        """
        return [validator.value for validator in self._capture_group_names.list]

    @property
    def capture_group_defaults(self) -> Optional[List[StringFormatterValidator]]:
        """
        Optional. List of string format validators to use for capture group defaults if a
        source variable cannot be matched. The list's length must be equal to the number of match
        capture groups.
        """
        return self._capture_group_defaults.list if self.has_defaults else None

    @property
    def has_defaults(self) -> bool:
        """
        Returns
        -------
        True if a validation exception should be raised if not captured. False otherwise.
        """
        return self._capture_group_defaults is not None


class FromSourceVariablesRegex(StrictDictValidator):

    _optional_keys = Entry.source_variables()
    _allow_extra_keys = True

    def __init__(self, name, value):
        super().__init__(name, value)
        self.variable_capture_dict: Dict[str, VariableRegex] = {
            key: self._validate_key(key=key, validator=VariableRegex) for key in self._keys
        }


class RegexOptions(OptionsDictValidator):
    r"""
    Performs regex matching on an entry's source or override variables. Regex can be used to filter
    entries from proceeding with download or capture groups to create new source variables.

    NOTE that YAML differentiates between single-quote (``'``) and double-quote (``"``), which can
    affect regex. Double-quote implies string literals, i.e. ``"\n"`` is the literal chars ``\n``,
    whereas single-quote, ``'\n'`` gets evaluated to a new line. To escape ``\`` when using
    single-quote, use ``\\``. This is necessary if you want your regex to be something like
    ``\d\n`` to match a number and adjacent new-line. It must be written as ``\\d\n``.

    If you want to regex-search multiple source variables to create a logical OR effect, you can
    create an override variable that contains the concatenation of them, and search that with regex.
    For example, creating the override variable ``"title_and_description": "{title} {description}"``
    and using ``title_and_description`` can regex match/exclude from either ``title`` or
    ``description``.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           regex:
             # By default, if any match fails and has no defaults, the entry will
             # be skipped. If False, ytdl-sub will error and stop all downloads
             # from proceeding.
             skip_if_match_fails: True

             from:
               # For each entry's `title` value...
               title:
                 # Perform this regex match on it to act as a filter.
                 # This will only download videos with "[Official Video]" in it. Note that we
                 # double backslash to make YAML happy
                 match:
                   - '\\[Official Video\\]'

               # For each entry's `description` value...
               description:
                 # Match with capture groups and defaults.
                 # This tries to scrape a date from the description and produce new
                 # source variables
                 match:
                   - '([0-9]{4})-([0-9]{2})-([0-9]{2})'
                 # Exclude any entry where the description contains #short
                 exclude:
                   - '#short'

                 # Each capture group creates these new source variables, respectively,
                 # as well a sanitized version, i.e. `captured_upload_year_sanitized`
                 capture_group_names:
                   - "captured_upload_year"
                   - "captured_upload_month"
                   - "captured_upload_day"

                 # And if the string does not match, use these as respective default
                 # values for the new source variables.
                 capture_group_defaults:
                   - "{upload_year}"
                   - "{upload_month}"
                   - "{upload_day}"
    """

    _required_keys = {"from"}
    _optional_keys = {"skip_if_match_fails"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate regex
        """
        if isinstance(value, dict):
            value["from"] = value.get("from", {})
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)
        self._from = self._validate_key(key="from", validator=FromSourceVariablesRegex)
        self._skip_if_match_fails: bool = self._validate_key_if_present(
            key="skip_if_match_fails", validator=BoolValidator, default=True
        ).value

    @property
    def skip_if_match_fails(self) -> Optional[bool]:
        """
        Defaults to True. If True, when any match fails and has no defaults, the entry will be
        skipped. If False, ytdl-sub will error and all downloads will not proceed.
        """
        return self._skip_if_match_fails

    def validate_with_variables(
        self, source_variables: List[str], override_variables: Dict[str, str]
    ) -> None:
        """
        Ensures each source variable capture group is valid

        Parameters
        ----------
        source_variables
            Available source variables when running the plugin
        override_variables
            Available override variables when running the plugin
        """
        for key, regex_options in self.source_variable_capture_dict.items():
            # Ensure each variable getting captured is a source variable
            if key not in source_variables and key not in override_variables:
                raise self._validation_exception(
                    f"cannot regex capture '{key}' because it is not a source or override variable"
                )

            # Ensure the capture group names are not existing source/override variables
            for capture_group_name in regex_options.capture_group_names:
                if capture_group_name in source_variables:
                    raise self._validation_exception(
                        f"'{capture_group_name}' cannot be used as a capture group name because it "
                        f"is a source variable"
                    )
                if capture_group_name in override_variables:
                    raise self._validation_exception(
                        f"'{capture_group_name}' cannot be used as a capture group name because it "
                        f"is an override variable"
                    )

    @property
    def source_variable_capture_dict(self) -> Dict[str, VariableRegex]:
        """
        Returns
        -------
        Dict of { source variable: capture options }
        """
        return self._from.variable_capture_dict

    def added_source_variables(self) -> List[str]:
        """
        Returns
        -------
        List of new source variables created via regex capture
        """
        added_source_vars: List[str] = []
        for regex_options in self.source_variable_capture_dict.values():
            added_source_vars.extend(regex_options.capture_group_names)
            added_source_vars.extend(
                f"{capture_group_name}_sanitized"
                for capture_group_name in regex_options.capture_group_names
            )

        return added_source_vars


class RegexPlugin(Plugin[RegexOptions]):
    plugin_options_type = RegexOptions
    priority = PluginPriority(
        modify_entry=PluginPriority.MODIFY_ENTRY_AFTER_SPLIT + 0,
    )

    @classmethod
    def _add_processed_regex_variable_name(cls, entry: Entry, source_var: str) -> None:
        if not entry.kwargs_contains(YTDL_SUB_REGEX_SOURCE_VARS):
            entry.add_kwargs({YTDL_SUB_REGEX_SOURCE_VARS: []})

        entry.kwargs(YTDL_SUB_REGEX_SOURCE_VARS).append(source_var)

    @classmethod
    def _contains_processed_regex_variable(cls, entry: Entry, variable_name: str) -> bool:
        return variable_name in entry.kwargs_get(YTDL_SUB_REGEX_SOURCE_VARS, [])

    def _try_skip_entry(self, entry: Entry, variable_name: str) -> None:
        # Skip the entry if toggled
        if self.plugin_options.skip_if_match_fails:
            logger.info(
                "Regex failed to match '%s' from '%s', skipping.",
                variable_name,
                entry.title,
            )
            return None

        # Otherwise, error
        raise RegexNoMatchException(f"Regex failed to match '{variable_name}' from '{entry.title}'")

    def _can_process_at_metadata_stage(self, entry: Entry, variable_name: str) -> bool:
        # If the variable is an override...
        if variable_name in self.overrides.dict:
            # Try to see if it can resolve
            try:
                self.overrides.apply_formatter(
                    formatter=self.overrides.dict[variable_name],
                    entry=entry,
                )
            # If it can not from missing variables (from post-metadata stage), return False
            except StringFormattingVariableNotFoundException:
                return False
        # If it is a source variable and not present, return false
        elif variable_name not in entry.to_dict():
            return False

        return True

    def _get_regex_input_string(self, entry: Entry, variable_name: str) -> str:
        # Apply override formatter if it's an override
        if variable_name in self.overrides.dict:
            return self.overrides.apply_formatter(
                formatter=self.overrides.dict[variable_name],
                entry=entry,
            )
        # Otherwise pluck from the entry's source variable
        return entry.to_dict()[variable_name]

    def _modify_entry_metadata(self, entry: Entry, is_metadata_stage: bool) -> Optional[Entry]:
        """
        Parameters
        ----------
        entry
            Entry to add source variables to
        is_metadata_stage
            Whether this is called at the metadata stage or modify stage

        Returns
        -------
        Entry with regex capture variables added to its source variables

        Raises
        ------
        ValidationException
            If no capture and no defaults
        """
        # Iterate each source var to capture and add to the entry
        for (
            variable_name,
            regex_options,
        ) in self.plugin_options.source_variable_capture_dict.items():

            # Record which regex source variables are processed, to
            # process as many variables as possible in the metadata stage, then the rest
            # after the media file has been downloaded.
            if self._contains_processed_regex_variable(entry, variable_name):
                continue

            # If it's the metadata stage, and it can't be processed, skip until post-metadata
            if is_metadata_stage and not self._can_process_at_metadata_stage(
                entry=entry, variable_name=variable_name
            ):
                continue

            self._add_processed_regex_variable_name(entry, variable_name)

            regex_input_str = self._get_regex_input_string(
                entry=entry,
                variable_name=variable_name,
            )

            if (
                regex_options.exclude is not None
                and regex_options.exclude.match_any(input_str=regex_input_str) is not None
            ):
                return self._try_skip_entry(entry=entry, variable_name=variable_name)

            # If match is present
            if regex_options.match is not None:
                maybe_capture = regex_options.match.match_any(input_str=regex_input_str)

                # And nothing matched
                if maybe_capture is None:
                    # and no defaults
                    if not regex_options.has_defaults:
                        return self._try_skip_entry(entry=entry, variable_name=variable_name)

                    # otherwise, use defaults (apply them using the original entry source dict)
                    source_variables_and_overrides_dict = dict(
                        entry.to_dict(), **self.overrides.dict_with_format_strings
                    )

                    # add both the default...
                    entry.add_variables(
                        variables_to_add={
                            regex_options.capture_group_names[i]: default.apply_formatter(
                                variable_dict=source_variables_and_overrides_dict
                            )
                            for i, default in enumerate(regex_options.capture_group_defaults)
                        },
                    )
                    # and sanitized default
                    entry.add_variables(
                        variables_to_add={
                            f"{regex_options.capture_group_names[i]}_sanitized": sanitize_filename(
                                default.apply_formatter(
                                    variable_dict=source_variables_and_overrides_dict
                                )
                            )
                            for i, default in enumerate(regex_options.capture_group_defaults)
                        },
                    )
                # There is a capture, add the source variables to the entry as
                # {source_var}_capture_1, {source_var}_capture_2, ...
                else:
                    # Add the value...
                    entry.add_variables(
                        variables_to_add={
                            regex_options.capture_group_names[i]: capture
                            for i, capture in enumerate(maybe_capture)
                        },
                    )
                    # And the sanitized value
                    entry.add_variables(
                        variables_to_add={
                            f"{regex_options.capture_group_names[i]}_sanitized": sanitize_filename(
                                capture
                            )
                            for i, capture in enumerate(maybe_capture)
                        },
                    )

        return entry

    def modify_entry_metadata(self, entry: Entry) -> Optional[Entry]:
        """
        Perform regex at the metadata stage
        """
        return self._modify_entry_metadata(entry, is_metadata_stage=True)

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        """
        Perform regex at the metadata stage
        """
        return self._modify_entry_metadata(entry, is_metadata_stage=False)
