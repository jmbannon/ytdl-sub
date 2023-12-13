import copy
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin_mapping import PluginMapping
from ytdl_sub.config.plugin.plugin_operation import PluginOperation
from ytdl_sub.config.plugin.preset_plugins import PresetPlugins
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.validators.options import OptionsValidator
from ytdl_sub.downloaders.url.validators import MultiUrlValidator
from ytdl_sub.entries.script.variable_scripts import VARIABLE_SCRIPTS
from ytdl_sub.script.script import Script
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.validators.string_formatter_validators import validate_formatters


def _get_added_variables(plugins: PresetPlugins, downloader_options: MultiUrlValidator) -> Set[str]:
    added_variables: Set[str] = set()
    options: List[OptionsValidator] = plugins.plugin_options
    options.append(downloader_options)

    for plugin_options in options:
        for plugin_added_variables in plugin_options.added_source_variables(
            unresolved_variables=set()
        ).values():
            added_variables |= set(plugin_added_variables)

    return added_variables


def _override_variables(overrides: Overrides) -> Set[str]:
    return set(list(overrides.initial_variables(unresolved_variables={}).keys()))


def _entry_variables() -> Set[str]:
    return set(list(VARIABLE_SCRIPTS.keys()))


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

    def initialize_overrides(self, overrides: Overrides) -> "VariableValidation":
        override_variables = _override_variables(overrides)
        entry_variables = _entry_variables()

        # Set unresolved as variables that are added but do not exist as entry/override variables
        self.unresolved_variables = (
            _get_added_variables(plugins=self.plugins, downloader_options=self.downloader_options)
            - override_variables
            - entry_variables
        )

        # Initialize overrides with unresolved variables to throw an error
        overrides = overrides.initialize_script(
            unresolved_variables={
                var_name: f"{{%throw('Plugin variable {var_name} has not been created yet')}}"
                for var_name in self.unresolved_variables
            }
        )

        # copy the script and mock entry variables
        self.script = copy.deepcopy(overrides.script).add(
            ScriptUtils.add_dummy_variables(entry_variables)
        )
        self.resolved_variables = self.script.variable_names - self.unresolved_variables

        return self

    def _update_script(self) -> None:
        _ = self.script.resolve(unresolvable=self.unresolved_variables, update=True)

    def _add_variables(self, plugin_op: PluginOperation, options: OptionsValidator) -> Set[str]:
        added_variables = options.added_source_variables(
            unresolved_variables=self.unresolved_variables
        ).get(plugin_op, set())

        if added_variables:
            for added_variable in added_variables:
                if added_variable in self.resolved_variables:
                    raise ValidationException(
                        f"Tried added the variable '{added_variable}', but it already "
                        f"exists as a defined variable."
                    )

            self.script.add(ScriptUtils.add_dummy_variables(added_variables))
            self.unresolved_variables -= added_variables

        return added_variables

    def ensure_proper_usage(self) -> None:
        """
        Validate variables resolve as plugins are executed, and return
        a mock script which contains actualized added variables from the plugins
        """
        self._add_variables(PluginOperation.DOWNLOADER, options=self.downloader_options)

        # Metadata variables to be added
        for plugin_options in PluginMapping.order_options_by(
            self.plugins.zipped(), PluginOperation.MODIFY_ENTRY_METADATA
        ):
            self._add_variables(PluginOperation.MODIFY_ENTRY_METADATA, options=plugin_options)

        self._update_script()
        for plugin_options in PluginMapping.order_options_by(
            self.plugins.zipped(), PluginOperation.MODIFY_ENTRY
        ):
            added = self._add_variables(PluginOperation.MODIFY_ENTRY, options=plugin_options)
            if added:
                self._update_script()

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
