import copy
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from mergedeep import mergedeep

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset_class_mappings import DownloadStrategyMapping
from ytdl_sub.config.preset_class_mappings import PluginMapping
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.config.preset_options import YTDLOptions
from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.yaml import load_yaml
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesDictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import DictValidator
from ytdl_sub.validators.validators import ListValidator
from ytdl_sub.validators.validators import StringListValidator
from ytdl_sub.validators.validators import StringValidator
from ytdl_sub.validators.validators import Validator

PRESET_KEYS = {
    "preset",
    "output_options",
    "ytdl_options",
    "overrides",
    *DownloadStrategyMapping.sources(),
    *PluginMapping.plugins(),
}


class PresetPlugins:
    _TPluginOptions = TypeVar("_TPluginOptions", bound=PluginOptions)

    def __init__(self):
        self.plugin_types: List[Type[Plugin]] = []
        self.plugin_options: List[PluginOptions] = []

    def add(self, plugin_type: Type[Plugin], plugin_options: PluginOptions) -> "PresetPlugins":
        """
        Add a pair of plugin type and options to the list
        """
        self.plugin_types.append(plugin_type)
        self.plugin_options.append(plugin_options)
        return self

    def zipped(self) -> Iterable[Tuple[Type[Plugin], PluginOptions]]:
        """
        Returns
        -------
        Plugin and PluginOptions zipped
        """
        return zip(self.plugin_types, self.plugin_options)

    def get(self, plugin_type: Type[_TPluginOptions]) -> Optional[_TPluginOptions]:
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


class DownloadStrategyValidator(StrictDictValidator):
    """
    Ensures a download strategy exists for a source. Does not validate any more than that.
    The respective Downloader's option validator will do that.
    """

    # All media sources must define a download strategy
    _required_keys = {"download_strategy"}

    # Extra fields will be strict-validated using other StictDictValidators
    _allow_extra_keys = True

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.download_strategy_name = self._validate_key(
            key="download_strategy",
            validator=StringValidator,
        ).value

    def get(self, downloader_source: str) -> Type[Downloader]:
        """
        Parameters
        ----------
        downloader_source:
            Name of the download source

        Returns
        -------
        The downloader class
        """
        try:
            return DownloadStrategyMapping.get(
                source=downloader_source, download_strategy=self.download_strategy_name
            )
        except ValueError as value_exc:
            raise self._validation_exception(error_message=value_exc)


class Preset(StrictDictValidator):
    # Have all present keys optional since parent presets could not have all the
    # required keys. They will get validated in the init after the mergedeep of dicts
    # and ensure required keys are present.
    _optional_keys = PRESET_KEYS

    @property
    def _source_variables(self) -> List[str]:
        return self.downloader.downloader_entry_type.source_variables()

    def __validate_and_get_downloader(self, downloader_source: str) -> Type[Downloader]:
        return self._validate_key(key=downloader_source, validator=DownloadStrategyValidator).get(
            downloader_source=downloader_source
        )

    def __validate_and_get_downloader_options(
        self, downloader_source: str, downloader: Type[Downloader]
    ) -> DownloaderValidator:
        # Remove the download_strategy key before validating it against the downloader options
        # TODO: make this cleaner
        del self._dict[downloader_source]["download_strategy"]
        return self._validate_key(
            key=downloader_source, validator=downloader.downloader_options_type
        )

    def __validate_and_get_downloader_and_options(
        self,
    ) -> Tuple[Type[Downloader], DownloaderValidator]:
        downloader: Optional[Type[Downloader]] = None
        download_options: Optional[DownloaderValidator] = None
        downloader_sources = DownloadStrategyMapping.sources()

        for key in self._keys:
            # skip if the key is not a download source
            if key not in downloader_sources:
                continue

            # Ensure there are not multiple sources, i.e. youtube and soundcloud
            if downloader:
                raise self._validation_exception(
                    f"'{self._name}' can only have one of the following sources: "
                    f"{', '.join(downloader_sources)}"
                )

            downloader = self.__validate_and_get_downloader(downloader_source=key)
            download_options = self.__validate_and_get_downloader_options(
                downloader_source=key, downloader=downloader
            )

        # If downloader was not set, error since it is required
        if not downloader:

            raise self._validation_exception(
                f"'{self._name} must have one of the following sources: "
                f"{', '.join(downloader_sources)}"
            )

        return downloader, download_options

    def __validate_and_get_plugins(self) -> PresetPlugins:
        preset_plugins = PresetPlugins()

        for key in self._keys:
            if key not in PluginMapping.plugins():
                continue

            plugin = PluginMapping.get(plugin=key)
            plugin_options = self._validate_key(key=key, validator=plugin.plugin_options_type)

            preset_plugins.add(plugin_type=plugin, plugin_options=plugin_options)

        return preset_plugins

    def __validate_added_variables(self):
        source_variables = copy.deepcopy(self._source_variables)

        # Validate added download option variables here since plugins could subsequently use them
        self.downloader_options.validate_with_variables(
            source_variables=source_variables,
            override_variables=self.overrides.dict_with_format_strings,
        )
        source_variables.extend(self.downloader_options.added_source_variables())

        for _, plugin_options in sorted(
            self.plugins.zipped(), key=lambda pl: pl[0].priority.modify_entry
        ):
            # Validate current plugin using source + added plugin variables
            plugin_options.validate_with_variables(
                source_variables=source_variables,
                override_variables=self.overrides.dict_with_format_strings,
            )

            # Extend existing source variables with ones created from this plugin
            source_variables.extend(plugin_options.added_source_variables())

    def __validate_override_string_formatter_validator(
        self,
        formatter_validator: Union[StringFormatterValidator, OverridesStringFormatterValidator],
    ):
        # Set the formatter variables to be the overrides
        variable_dict = copy.deepcopy(self.overrides.dict_with_format_strings)

        # If the formatter supports source variables, set the formatter variables to include
        # both source and override variables
        if not isinstance(formatter_validator, OverridesStringFormatterValidator):
            source_variables = {
                source_var: "dummy_string"
                for source_var in self._source_variables
                + self.downloader_options.added_source_variables()
            }
            variable_dict = dict(source_variables, **variable_dict)

            # For all plugins, add in any extra added source variables
            for plugin_options in self.plugins.plugin_options:
                added_plugin_variables = {
                    source_var: "dummy_string"
                    for source_var in plugin_options.added_source_variables()
                }
                # sanity check plugin variables do not override source variables
                expected_len = len(variable_dict) + len(added_plugin_variables)
                variable_dict = dict(variable_dict, **added_plugin_variables)

                assert (
                    len(variable_dict) == expected_len
                ), "plugin variables overwrote source variables"

        _ = formatter_validator.apply_formatter(variable_dict=variable_dict)

    def __recursive_preset_validate(
        self,
        validator: Optional[Validator] = None,
    ) -> None:
        """
        Ensure all OverridesStringFormatterValidator's only contain variables from the overrides
        and resolve.
        """
        if validator is None:
            validator = self

        if isinstance(validator, DictValidator):
            # pylint: disable=protected-access
            # Usage of protected variables in other validators is fine. The reason to keep
            # them protected is for readability when using them in subscriptions.
            for validator_value in validator._validator_dict.values():
                self.__recursive_preset_validate(validator_value)
            # pylint: enable=protected-access
        elif isinstance(validator, ListValidator):
            for list_value in validator.list:
                self.__recursive_preset_validate(list_value)
        elif isinstance(validator, (StringFormatterValidator, OverridesStringFormatterValidator)):
            self.__validate_override_string_formatter_validator(validator)
        elif isinstance(validator, (DictFormatterValidator, OverridesDictFormatterValidator)):
            for validator_value in validator.dict.values():
                self.__validate_override_string_formatter_validator(validator_value)

    def __merge_parent_preset_dicts_if_present(self, config: ConfigFile):
        parent_preset_validator = self._validate_key_if_present(
            key="preset", validator=StringListValidator
        )

        if parent_preset_validator is None:
            return

        presets_to_merge: List[Dict] = []
        for parent_preset in [preset.value for preset in parent_preset_validator.list]:
            sub_parent_presets: Dict[str, Dict] = {}

            while parent_preset:
                # Make sure the parent preset actually exists
                if parent_preset not in config.presets.keys:
                    raise self._validation_exception(
                        f"preset '{parent_preset}' does not exist in the provided config. "
                        f"Available presets: {', '.join(config.presets.keys)}"
                    )

                # Make sure we do not hit an infinite loop
                if parent_preset in sub_parent_presets:
                    raise self._validation_exception(
                        f"preset loop detected with the preset '{parent_preset}'"
                    )

                parent_preset_dict = copy.deepcopy(config.presets.dict[parent_preset])

                sub_parent_presets[parent_preset] = parent_preset_dict
                parent_preset = parent_preset_dict.get("preset")

            # Extend reversed, so top-most parents are first
            if sub_parent_presets:
                presets_to_merge.extend(reversed(sub_parent_presets.values()))

        # Append this preset (the subscription) last
        presets_to_merge.append(copy.deepcopy(self._value))

        # Merge all of the presets
        self._value = mergedeep.merge({}, *presets_to_merge, strategy=mergedeep.Strategy.REPLACE)

    def __init__(self, config: ConfigFile, name: str, value: Any):
        super().__init__(name=name, value=value)

        # Perform the merge of parent presets before validating any keys
        self.__merge_parent_preset_dicts_if_present(config=config)

        self.downloader, self.downloader_options = self.__validate_and_get_downloader_and_options()

        self.output_options = self._validate_key(
            key="output_options",
            validator=OutputOptions,
        )

        self.ytdl_options = self._validate_key(
            key="ytdl_options", validator=YTDLOptions, default={}
        )

        self.overrides = self._validate_key(key="overrides", validator=Overrides, default={})
        self.plugins: PresetPlugins = self.__validate_and_get_plugins()
        self.__validate_added_variables()

        # After all options are initialized, perform a recursive post-validate that requires
        # values from multiple validators
        self.__recursive_preset_validate()

    @property
    def name(self) -> str:
        """
        Returns
        -------
        Name of the preset
        """
        return self._name

    @classmethod
    def from_dict(cls, config: ConfigFile, preset_name: str, preset_dict: Dict) -> "Preset":
        """
        Parameters
        ----------
        config:
            Validated instance of the config
        preset_name:
            Name of the preset
        preset_dict:
            The preset config in dict format

        Returns
        -------
        The Subscription validator
        """
        return cls(config=config, name=preset_name, value=preset_dict)

    @classmethod
    def from_file_path(cls, config: ConfigFile, subscription_path: str) -> List["Preset"]:
        """
        Parameters
        ----------
        config:
            Validated instance of the config
        subscription_path:
            File path to the subscription yaml file

        Returns
        -------
        List of presets, for each one in the subscription yaml
        """
        subscription_dict = load_yaml(file_path=subscription_path)

        subscriptions: List["Preset"] = []
        for subscription_key, subscription_object in subscription_dict.items():
            subscriptions.append(
                Preset.from_dict(
                    config=config,
                    preset_name=subscription_key,
                    preset_dict=subscription_object,
                )
            )

        return subscriptions
