from collections import defaultdict
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.plugin.plugin_operation import PluginOperation
from ytdl_sub.config.validators.options import ToggleableOptionsDictValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.script.parser import parse
from ytdl_sub.script.utils.exceptions import RuntimeException
from ytdl_sub.utils.exceptions import RegexNoMatchException
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.regex_validator import RegexListValidator
from ytdl_sub.validators.source_variable_validator import SourceVariableNameListValidator
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import ListFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import BoolValidator
from ytdl_sub.validators.validators import DictValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

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


class FromSourceVariablesRegex(DictValidator):
    def __init__(self, name, value):
        super().__init__(name, value)
        self.variable_capture_dict: Dict[str, VariableRegex] = {
            key: self._validate_key(key=key, validator=VariableRegex) for key in self._keys
        }


class RegexOptions(ToggleableOptionsDictValidator):
    r"""
    .. attention::

       This plugin will eventually be deprecated and replaced by scripting functions.
       You can replicate the example below using the following.

       .. code-block:: yaml

          # Only includes videos with 'Official Video'
          filter_include:
            - >-
              { %contains( %lower(title), "official video" ) }

          # Excludes videos with '#short' in its description
          filter_exclude:
            - >-
              { %contains( %lower(description), '#short' ) }

          # Creates a capture array with defaults, and assigns
          # each capture group to its own variable
          overrides:
            description_date_capture: >-
              {
                %regex_capture_many_with_defaults(
                  description,
                  [ "([0-9]{4})-([0-9]{2})-([0-9]{2})" ],
                  [ upload_year, upload_month, upload_day ]
                )
              }
            captured_upload_year: >-
              { %array_at(description_date_capture, 1) }
            captured_upload_month: >-
              { %array_at(description_date_capture, 2) }
            captured_upload_day: >-
              { %array_at(description_date_capture, 3) }

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

    :Usage:

    .. code-block:: yaml

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
    _optional_keys = {"enable", "skip_if_match_fails"}

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

        # Variables added by the regex plugin
        self._added_variable_names: Set[str] = set()

    @property
    def skip_if_match_fails(self) -> Optional[bool]:
        """
        :expected type: Optional[Boolean]
        :description:
          Defaults to True. If True, when any match fails and has no defaults, the entry will be
          skipped. If False, ytdl-sub will error and all downloads will not proceed.
        """
        return self._skip_if_match_fails

    @property
    def source_variable_capture_dict(self) -> Dict[str, VariableRegex]:
        """
        Returns
        -------
        Dict of { source variable: capture options }
        """
        return self._from.variable_capture_dict

    @classmethod
    def _can_resolve(
        cls, unresolved_variables: Set[str], input_variable_name: str, regex_options: VariableRegex
    ) -> bool:
        if input_variable_name in unresolved_variables:
            return False
        for capture_group_default in regex_options.capture_group_defaults or []:
            parsed_default = parse(capture_group_default.format_string)
            if parsed_default.variables and parsed_default.variables.issubset(unresolved_variables):
                return False
        return True

    def added_variables(
        self,
        resolved_variables: Set[str],
        unresolved_variables: Set[str],
        plugin_op: PluginOperation,
    ) -> Dict[PluginOperation, Set[str]]:
        """
        Returns
        -------
        List of new source variables created via regex capture
        """
        added_source_vars: Dict[PluginOperation, Set[str]] = {
            PluginOperation.MODIFY_ENTRY_METADATA: set(),
            PluginOperation.MODIFY_ENTRY: set(),
        }
        for input_variable_name, regex_options in self.source_variable_capture_dict.items():
            variables_to_add = set(regex_options.capture_group_names)

            if plugin_op != PluginOperation.ANY and input_variable_name not in (
                resolved_variables | unresolved_variables
            ):
                raise self._validation_exception(
                    f"cannot regex capture '{input_variable_name}' because it is not a"
                    " defined variable."
                )
            if (
                plugin_op.value >= PluginOperation.MODIFY_ENTRY.value
                and input_variable_name in unresolved_variables
            ):
                raise self._validation_exception(
                    f"cannot regex capture '{input_variable_name}' because it is not "
                    f"computed until later in execution."
                )

            if plugin_op == PluginOperation.ANY:
                added_source_vars[PluginOperation.MODIFY_ENTRY_METADATA] |= variables_to_add
                self._added_variable_names |= variables_to_add
                continue

            if not self._can_resolve(
                unresolved_variables=unresolved_variables,
                input_variable_name=input_variable_name,
                regex_options=regex_options,
            ):
                continue

            for capture_group_name in regex_options.capture_group_names:
                if capture_group_name in (resolved_variables - self._added_variable_names):
                    raise self._validation_exception(
                        f"cannot use '{capture_group_name}' as a capture group name because it is "
                        f"an already defined variable."
                    )
            added_source_vars[plugin_op] |= set(regex_options.capture_group_names)

        return added_source_vars


class RegexPlugin(Plugin[RegexOptions]):
    plugin_options_type = RegexOptions

    def __init__(
        self,
        options: RegexOptions,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        super().__init__(
            options=options,
            overrides=overrides,
            enhanced_download_archive=enhanced_download_archive,
        )
        # Lookup of entry id to processed regex variables
        self._processed_regex_vars: Dict[str, Set[str]] = defaultdict(set)

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

    @classmethod
    def _can_process_at_metadata_stage(cls, entry: Entry, variable_name: str) -> bool:
        # Try to see if it can resolve
        try:
            _ = entry.script.get(variable_name)
            return True
        # If it can not from missing variables (from post-metadata stage), return False
        except RuntimeException:
            return False

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
            if variable_name in self._processed_regex_vars[entry.ytdl_uid()]:
                continue

            # If it's the metadata stage, and it can't be processed, skip until post-metadata
            if is_metadata_stage and not self._can_process_at_metadata_stage(
                entry=entry, variable_name=variable_name
            ):
                continue

            self._processed_regex_vars[entry.ytdl_uid()].add(variable_name)
            regex_input_str = str(entry.script.get(variable_name))

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

                    # add both the default...
                    entry.add(
                        {
                            regex_options.capture_group_names[i]: self.overrides.apply_formatter(
                                formatter=default, entry=entry
                            )
                            for i, default in enumerate(regex_options.capture_group_defaults)
                        }
                    )
                # There is a capture, add the source variables to the entry as
                # {source_var}_capture_1, {source_var}_capture_2, ...
                else:
                    entry.add(
                        {
                            regex_options.capture_group_names[i]: capture
                            for i, capture in enumerate(maybe_capture)
                        }
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
