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
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.validators.string_formatter_validators import validate_formatters


class VariableValidation:
    @classmethod
    def _get_added_variables(
        cls, plugins: PresetPlugins, downloader_options: MultiUrlValidator
    ) -> Set[str]:
        added_variables: Set[str] = set()
        options: List[OptionsValidator] = plugins.plugin_options
        options.append(downloader_options)

        for plugin_options in options:
            for plugin_added_variables in plugin_options.added_source_variables(
                unresolved_variables=set()
            ).values():
                added_variables |= set(plugin_added_variables)

        return added_variables

    def __init__(
        self,
        downloader_options: MultiUrlValidator,
        output_options: OutputOptions,
        plugins: PresetPlugins,
    ):
        self.script: Optional[Script] = None
        self.resolved_variables: Set[str] = set()

        self.downloader_options = downloader_options
        self.output_options = output_options
        self.plugins = plugins
        self.unresolved_variables = VariableValidation._get_added_variables(
            plugins=plugins, downloader_options=downloader_options
        )

    def initialize_overrides(self, overrides: Overrides) -> "VariableValidation":
        overrides = overrides.initialize_script(
            unresolved_variables={
                var_name: f"{{%throw('Plugin variable {var_name} has not been created yet')}}"
                for var_name in self.unresolved_variables
            }
        )
        self.script = copy.deepcopy(overrides.script).add(
            ScriptUtils.add_dummy_variables(list(VARIABLE_SCRIPTS.keys()))
        )
        self.resolved_variables = self.script.variable_names - self.unresolved_variables

        return self

    def ensure_proper_usage(self) -> None:
        """
        Validate variables resolve as plugins are executed, and return
        a mock script which contains actualized added variables from the plugins
        """

        added_variables: Set[str] = self.downloader_options.added_source_variables(
            self.unresolved_variables
        ).get(PluginOperation.DOWNLOADER, set())
        self.script.add(ScriptUtils.add_dummy_variables(added_variables))
        self.unresolved_variables -= added_variables

        for plugin_options in PluginMapping.order_options_by(
            self.plugins.zipped(), PluginOperation.MODIFY_ENTRY_METADATA
        ):
            added_variables = plugin_options.added_source_variables(
                unresolved_variables=self.unresolved_variables
            ).get(PluginOperation.MODIFY_ENTRY_METADATA, set())

            if added_variables:
                self.script.add(ScriptUtils.add_dummy_variables(added_variables))
                self.unresolved_variables -= added_variables

        _ = self.script.resolve(unresolvable=self.unresolved_variables, update=True)
        for plugin_options in PluginMapping.order_options_by(
            self.plugins.zipped(), PluginOperation.MODIFY_ENTRY
        ):
            added_variables = plugin_options.added_source_variables(
                unresolved_variables=self.unresolved_variables
            ).get(PluginOperation.MODIFY_ENTRY, set())

            if added_variables:
                self.script.add(ScriptUtils.add_dummy_variables(added_variables))
                self.unresolved_variables -= added_variables

                _ = self.script.resolve(unresolvable=self.unresolved_variables, update=True)

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
