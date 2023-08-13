import copy
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from mergedeep import mergedeep

from ytdl_sub.config.config_validator import ConfigValidator
from ytdl_sub.config.plugin import Plugin
from ytdl_sub.config.preset_class_mappings import PluginMapping
from ytdl_sub.config.preset_options import OptionsValidator
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.config.preset_options import TOptionsValidator
from ytdl_sub.config.preset_options import YTDLOptions
from ytdl_sub.downloaders.url.validators import MultiUrlValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.prebuilt_presets import PREBUILT_PRESET_NAMES
from ytdl_sub.prebuilt_presets import PUBLISHED_PRESET_NAMES
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.yaml import dump_yaml
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesDictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import DictValidator
from ytdl_sub.validators.validators import ListValidator
from ytdl_sub.validators.validators import StringListValidator
from ytdl_sub.validators.validators import Validator
from ytdl_sub.validators.validators import validation_exception

PRESET_KEYS = {
    "preset",
    "download",
    "output_options",
    "ytdl_options",
    "overrides",
    *PluginMapping.plugins(),
}

logger = Logger.get()


def _parent_preset_error_message(
    current_preset_name: str, parent_preset_name: str, presets: List[str]
) -> ValidationException:
    user_defined_presets = set(presets) - PREBUILT_PRESET_NAMES - {current_preset_name}

    return validation_exception(
        name=current_preset_name,
        error_message=f"preset '{parent_preset_name}' does not exist in the provided config.\n"
        f"Available prebuilt presets: {', '.join(sorted(PUBLISHED_PRESET_NAMES))}\n"
        f"Your presets: {', '.join(sorted(user_defined_presets))}",
    )


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

    def zipped(self) -> Iterable[Tuple[Type[Plugin], OptionsValidator]]:
        """
        Returns
        -------
        Plugin and PluginOptions zipped
        """
        return zip(self.plugin_types, self.plugin_options)

    def get(self, plugin_type: Type[TOptionsValidator]) -> Optional[TOptionsValidator]:
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


class _PresetShell(StrictDictValidator):
    # Have all present keys optional since parent presets could not have all the
    # required keys. They will get validated in the init after the mergedeep of dicts
    # and ensure required keys are present.
    _optional_keys = PRESET_KEYS


class Preset(_PresetShell):
    @classmethod
    def preset_partial_validate(cls, config: ConfigValidator, name: str, value: Any) -> None:
        """
        Partially validates a preset. Used to ensure every preset in a ConfigFile looks sane.
        Cannot fully validate each preset using the Preset init because required fields could
        be missing, which become filled in a child preset.

        Parameters
        ----------
        config
            Config that this preset belongs to
        name
            Preset name
        value
            Preset value

        Raises
        ------
        ValidationException
            If validation fails
        """
        # Ensure value is a dict
        _ = _PresetShell(name=name, value=value)
        assert isinstance(value, dict)

        parent_presets = StringListValidator(name=f"{name}.preset", value=value.get("preset", []))
        for parent_preset_name in parent_presets.list:
            if parent_preset_name.value not in config.presets.keys:
                raise _parent_preset_error_message(
                    current_preset_name=name,
                    parent_preset_name=parent_preset_name.value,
                    presets=config.presets.keys,
                )

        cls._partial_validate_key(name, value, "download", MultiUrlValidator)
        cls._partial_validate_key(name, value, "output_options", OutputOptions)
        cls._partial_validate_key(name, value, "ytdl_options", YTDLOptions)
        cls._partial_validate_key(name, value, "overrides", Overrides)

        for plugin_name in PluginMapping.plugins():
            cls._partial_validate_key(
                name,
                value,
                key=plugin_name,
                validator=PluginMapping.get(plugin_name).plugin_options_type,
            )

    @property
    def _source_variables(self) -> List[str]:
        return Entry.source_variables()

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

    def _get_presets_to_merge(
        self, parent_presets: str | List[str], seen_presets: List[str], config: ConfigValidator
    ) -> List[Dict]:
        presets_to_merge: List[Dict] = []

        if isinstance(parent_presets, str):
            parent_presets = [parent_presets]

        for parent_preset in reversed(parent_presets):
            # Make sure we do not hit an infinite loop
            if parent_preset in seen_presets:
                raise self._validation_exception(
                    f"preset loop detected with the preset '{parent_preset}'"
                )

            # Make sure the parent preset actually exists
            if parent_preset not in config.presets.keys:
                raise _parent_preset_error_message(
                    current_preset_name=self._name,
                    parent_preset_name=parent_preset,
                    presets=config.presets.keys,
                )

            parent_preset_dict = copy.deepcopy(config.presets.dict[parent_preset])
            presets_to_merge.append(parent_preset_dict)

            if "preset" in parent_preset_dict:
                presets_to_merge.extend(
                    self._get_presets_to_merge(
                        parent_presets=parent_preset_dict["preset"],
                        seen_presets=seen_presets + [parent_preset],
                        config=config,
                    )
                )

        return presets_to_merge

    def __merge_parent_preset_dicts_if_present(self, config: ConfigValidator):
        parent_preset_validator = self._validate_key_if_present(
            key="preset", validator=StringListValidator
        )
        if parent_preset_validator is None:
            return

        # Get list of all parent presets in depth-first search order, beginning with this preset
        presets_to_merge: List[Dict] = [copy.deepcopy(self._value)] + self._get_presets_to_merge(
            parent_presets=[preset.value for preset in parent_preset_validator.list],
            seen_presets=[],
            config=config,
        )

        # Merge all presets
        self._value = dict(
            mergedeep.merge({}, *reversed(presets_to_merge), strategy=mergedeep.Strategy.ADDITIVE)
        )

    def __init__(self, config: ConfigValidator, name: str, value: Any):
        super().__init__(name=name, value=value)

        # Perform the merge of parent presets before validating any keys
        self.__merge_parent_preset_dicts_if_present(config=config)

        self.downloader_options: MultiUrlValidator = self._validate_key(
            key="download", validator=MultiUrlValidator
        )

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
    def from_dict(cls, config: ConfigValidator, preset_name: str, preset_dict: Dict) -> "Preset":
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

    @property
    def yaml(self) -> str:
        """
        Returns
        -------
        Preset in YAML format
        """
        return dump_yaml({"presets": {self._name: self._value}})
