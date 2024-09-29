import copy
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin_mapping import PluginMapping
from ytdl_sub.config.plugin.plugin_operation import PluginOperation
from ytdl_sub.config.plugin.preset_plugins import PresetPlugins
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.validators.options import OptionsValidator
from ytdl_sub.downloaders.url.validators import MultiUrlValidator
from ytdl_sub.entries.variables.override_variables import REQUIRED_OVERRIDE_VARIABLE_NAMES
from ytdl_sub.script.script import Script
from ytdl_sub.script.script import _is_function
from ytdl_sub.utils.scriptable import BASE_SCRIPT
from ytdl_sub.validators.string_formatter_validators import to_variable_dependency_format_string
from ytdl_sub.validators.string_formatter_validators import validate_formatters

# Entry variables to mock during validation
_DUMMY_ENTRY_VARIABLES: Dict[str, str] = {
    name: to_variable_dependency_format_string(
        # pylint: disable=protected-access
        script=BASE_SCRIPT,
        parsed_format_string=BASE_SCRIPT._variables[name],
        # pylint: enable=protected-access
    )
    for name in BASE_SCRIPT.variable_names
}


def _add_dummy_variables(variables: Iterable[str]) -> Dict[str, str]:
    dummy_variables: Dict[str, str] = {}
    for var in variables:
        dummy_variables[var] = ""
        dummy_variables[f"{var}_sanitized"] = ""

    return dummy_variables


def _add_dummy_overrides(overrides: Overrides) -> Dict[str, str]:
    # Have the dummy override variable contain all variable deps that it uses in the string
    dummy_overrides: Dict[str, str] = {}
    for override_name in _override_variables(overrides):
        if _is_function(override_name):
            continue

        # pylint: disable=protected-access
        dummy_overrides[override_name] = to_variable_dependency_format_string(
            script=overrides.script, parsed_format_string=overrides.script._variables[override_name]
        )
        # pylint: enable=protected-access
    return dummy_overrides


def _get_added_and_modified_variables(
    plugins: PresetPlugins, downloader_options: MultiUrlValidator
) -> Iterable[Tuple[OptionsValidator, Set[str], Set[str]]]:
    """
    Iterates and returns the plugin options, added variables, modified variables
    """
    options: List[OptionsValidator] = plugins.plugin_options
    options.append(downloader_options)

    for plugin_options in options:
        added_variables: Set[str] = set()
        modified_variables: Set[str] = set()

        for plugin_added_variables in plugin_options.added_variables(
            unresolved_variables=set(),
        ).values():
            added_variables |= set(plugin_added_variables)

        for plugin_modified_variables in plugin_options.modified_variables().values():
            modified_variables = plugin_modified_variables

        yield plugin_options, added_variables, modified_variables


def _override_variables(overrides: Overrides) -> Set[str]:
    return set(list(overrides.initial_variables().keys()))


class VariableValidation:
    def __init__(
        self,
        downloader_options: MultiUrlValidator,
        output_options: OutputOptions,
        plugins: PresetPlugins,
    ):
        self.downloader_options = downloader_options
        self.output_options = output_options
        self.plugins = plugins

        self.script: Optional[Script] = None
        self.resolved_variables: Set[str] = set()
        self.unresolved_variables: Set[str] = set()

    def initialize_preset_overrides(self, overrides: Overrides) -> "VariableValidation":
        """
        Do some gymnastics to initialize the Overrides script.
        """
        override_variables = set(list(overrides.initial_variables().keys()))

        # Set resolved variables as all entry + override variables
        # at this point to generate every possible added/modified variable
        self.resolved_variables = set(_DUMMY_ENTRY_VARIABLES.keys()) | override_variables
        plugin_variables: Set[str] = set()

        for (
            plugin_options,
            added_variables,
            modified_variables,
        ) in _get_added_and_modified_variables(
            plugins=self.plugins,
            downloader_options=self.downloader_options,
        ):

            for added_variable in added_variables:
                if not overrides.ensure_added_plugin_variable_valid(added_variable=added_variable):
                    # pylint: disable=protected-access
                    raise plugin_options._validation_exception(
                        f"Cannot use the variable name {added_variable} because it exists as a"
                        " built-in ytdl-sub variable name."
                    )
                    # pylint: enable=protected-access

            # Set unresolved as variables that are added but do not exist as
            # entry/override variables since they are created at run-time
            self.unresolved_variables |= added_variables | modified_variables
            plugin_variables |= added_variables | modified_variables

        # Then update resolved variables to reflect that
        self.resolved_variables -= self.unresolved_variables

        # Initialize overrides with unresolved variables + modified variables to throw an error.
        # For modified variables, this is to prevent a resolve(update=True) to setting any
        # dependencies until it has been explicitly added
        overrides = overrides.initialize_script(unresolved_variables=self.unresolved_variables)

        # copy the script and mock entry variables
        self.script = copy.deepcopy(overrides.script)
        self.script.add(
            variables=_add_dummy_overrides(overrides=overrides)
            | _add_dummy_variables(variables=plugin_variables)
            | _DUMMY_ENTRY_VARIABLES
        )

        return self

    def _update_script(self) -> None:
        _ = self.script.resolve(unresolvable=self.unresolved_variables, update=True)

    def _add_subscription_override_variables(self) -> None:
        """
        Add dummy subscription variables for script validation
        """
        self.resolved_variables |= REQUIRED_OVERRIDE_VARIABLE_NAMES

    def _add_variables(self, plugin_op: PluginOperation, options: OptionsValidator) -> None:
        """
        Add dummy variables for script validation
        """
        added_variables = options.added_variables(
            unresolved_variables=self.unresolved_variables,
        ).get(plugin_op, set())
        modified_variables = options.modified_variables().get(plugin_op, set())

        resolved_variables = added_variables | modified_variables

        self.resolved_variables |= resolved_variables
        self.unresolved_variables -= resolved_variables

    def ensure_proper_usage(self) -> None:
        """
        Validate variables resolve as plugins are executed, and return
        a mock script which contains actualized added variables from the plugins
        """

        self._add_variables(PluginOperation.DOWNLOADER, options=self.downloader_options)
        self._add_subscription_override_variables()

        # Metadata variables to be added
        for plugin_options in PluginMapping.order_options_by(
            self.plugins.zipped(), PluginOperation.MODIFY_ENTRY_METADATA
        ):
            self._add_variables(PluginOperation.MODIFY_ENTRY_METADATA, options=plugin_options)

        for plugin_options in PluginMapping.order_options_by(
            self.plugins.zipped(), PluginOperation.MODIFY_ENTRY
        ):
            self._add_variables(PluginOperation.MODIFY_ENTRY, options=plugin_options)

            # Validate that any formatter in the plugin options can resolve
            validate_formatters(
                script=self.script,
                unresolved_variables=self.unresolved_variables,
                validator=plugin_options,
            )

        validate_formatters(
            script=self.script,
            unresolved_variables=self.unresolved_variables,
            validator=self.output_options,
        )

        assert not self.unresolved_variables
