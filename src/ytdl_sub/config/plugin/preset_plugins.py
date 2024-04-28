from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.validators.options import OptionsValidator
from ytdl_sub.config.validators.options import OptionsValidatorT


class PresetPlugins:
    def __init__(self):
        self.plugin_types: List[Type[Plugin]] = []
        self.plugin_options: List[OptionsValidator] = []

    def add(self, plugin_type: Type[Plugin], plugin_options: OptionsValidator) -> "PresetPlugins":
        """
        Add a pair of plugin type and options to the list
        """
        self.plugin_types.append(plugin_type)
        self.plugin_options.append(plugin_options)
        return self

    def zipped(self) -> List[Tuple[Type[Plugin], OptionsValidator]]:
        """
        Returns
        -------
        Plugin and PluginOptions zipped
        """
        return list(zip(self.plugin_types, self.plugin_options))

    def get(self, plugin_type: Type[OptionsValidatorT]) -> Optional[OptionsValidatorT]:
        """
        Parameters
        ----------
        plugin_type
            Fetch the plugin options for this type

        Returns
        -------
        Options of this plugin if they exit. Otherwise, return None.
        """
        plugin_option_types = [type(plugin_options) for plugin_options in self.plugin_options]
        if plugin_type in plugin_option_types:
            return self.plugin_options[plugin_option_types.index(plugin_type)]
        return None
