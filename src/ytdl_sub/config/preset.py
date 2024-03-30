import copy
from typing import Any
from typing import Dict
from typing import List

from mergedeep import mergedeep

from ytdl_sub.config.config_validator import ConfigValidator
from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.plugin_mapping import PluginMapping
from ytdl_sub.config.plugin.preset_plugins import PresetPlugins
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.preset_options import YTDLOptions
from ytdl_sub.config.validators.variable_validation import VariableValidation
from ytdl_sub.downloaders.url.validators import MultiUrlValidator
from ytdl_sub.prebuilt_presets import PREBUILT_PRESET_NAMES
from ytdl_sub.prebuilt_presets import PUBLISHED_PRESET_NAMES
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.yaml import dump_yaml
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.validators import StringListValidator
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

    def _validate_and_get_plugins(self) -> PresetPlugins:
        preset_plugins = PresetPlugins()

        for key in self._keys:
            if key not in PluginMapping.plugins():
                continue

            plugin = PluginMapping.get(plugin=key)
            plugin_options = self._validate_key(key=key, validator=plugin.plugin_options_type)

            preset_plugins.add(plugin_type=plugin, plugin_options=plugin_options)

        return preset_plugins

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

    def _merge_parent_preset_dicts_if_present(self, config: ConfigValidator):
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
        self._merge_parent_preset_dicts_if_present(config=config)

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

        self.plugins: PresetPlugins = self._validate_and_get_plugins()
        self.overrides = self._validate_key(key="overrides", validator=Overrides, default={})

        VariableValidation(
            downloader_options=self.downloader_options,
            output_options=self.output_options,
            plugins=self.plugins,
        ).initialize_preset_overrides(overrides=self.overrides).ensure_proper_usage()

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
