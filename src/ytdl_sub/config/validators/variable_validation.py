from typing import Dict

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin_mapping import PluginMapping
from ytdl_sub.config.plugin.plugin_operation import PluginOperation
from ytdl_sub.config.plugin.preset_plugins import PresetPlugins
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.validators.options import OptionsValidator
from ytdl_sub.downloaders.url.validators import MultiUrlValidator
from ytdl_sub.validators.string_formatter_validators import validate_formatters


class VariableValidation:
    def __init__(
        self,
        overrides: Overrides,
        downloader_options: MultiUrlValidator,
        output_options: OutputOptions,
        plugins: PresetPlugins,
    ):
        self.overrides = overrides
        self.downloader_options = downloader_options
        self.output_options = output_options
        self.plugins = plugins

        self.script = self.overrides.script
        self.unresolved_variables = self.plugins.get_all_variables(
            additional_options=[self.output_options, self.downloader_options]
        )

    def _add_variables(self, plugin_op: PluginOperation, options: OptionsValidator) -> None:
        """
        Add dummy variables for script validation
        """
        added_variables = options.added_variables(
            unresolved_variables=self.unresolved_variables,
        ).get(plugin_op, set())
        modified_variables = options.modified_variables().get(plugin_op, set())

        self.unresolved_variables -= added_variables | modified_variables

    def ensure_proper_usage(self) -> Dict:
        """
        Validate variables resolve as plugins are executed, and return
        a mock script which contains actualized added variables from the plugins
        """

        resolved_subscription: Dict = {}

        self._add_variables(PluginOperation.DOWNLOADER, options=self.downloader_options)

        # Always add output options first
        self._add_variables(PluginOperation.MODIFY_ENTRY_METADATA, options=self.output_options)

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
            resolved_subscription |= validate_formatters(
                script=self.script,
                unresolved_variables=self.unresolved_variables,
                validator=plugin_options,
            )

        resolved_subscription |= validate_formatters(
            script=self.script,
            unresolved_variables=self.unresolved_variables,
            validator=self.output_options,
        )

        # TODO: make this a function
        raw_download_output = validate_formatters(
            script=self.script,
            unresolved_variables=self.unresolved_variables,
            validator=self.downloader_options.urls,
        )
        resolved_subscription["download"] = []
        for url_output in raw_download_output["download"]:
            if isinstance(url_output["url"], list):
                url_output["url"] = [url for url in url_output["url"] if bool(url)]

            if url_output["url"]:
                resolved_subscription["download"].append(url_output)

        assert not self.unresolved_variables
        return resolved_subscription
