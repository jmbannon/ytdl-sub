import copy
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

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
from ytdl_sub.utils.exceptions import StringFormattingVariableNotFoundException
from ytdl_sub.utils.yaml import load_yaml
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.validators import DictValidator
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

    def __validate_and_get_plugins(self) -> List[Tuple[Type[Plugin], PluginOptions]]:
        plugins: List[Tuple[Type[Plugin], PluginOptions]] = []

        for key in self._keys:
            if key not in PluginMapping.plugins():
                continue

            plugin = PluginMapping.get(plugin=key)
            plugin_options = self._validate_key(key=key, validator=plugin.plugin_options_type)

            plugins.append((plugin, plugin_options))

        return plugins

    def __validate_override_string_formatter_validator(
        self, formatter_validator: OverridesStringFormatterValidator
    ):
        # Gather all resolvable override variables
        resolvable_override_variables: List[str] = []
        for name, override_variable in self.overrides.dict.items():
            try:
                _ = override_variable.apply_formatter(self.overrides.dict_with_format_strings)
            except StringFormattingVariableNotFoundException:
                continue
            resolvable_override_variables.append(name)

        for variable_name in formatter_validator.format_variables:
            if variable_name not in resolvable_override_variables:
                raise StringFormattingVariableNotFoundException(
                    f"This variable can only use override variables that resolve without needing "
                    f"variables from a downloaded file. The only override variables defined that "
                    f"meet this condition are: {', '.join(sorted(resolvable_override_variables))}"
                )

    def __recursive_preset_validate(
        self, validator_dict: Optional[Dict[str, Validator]] = None
    ) -> None:
        """
        Ensure all OverridesStringFormatterValidator's only contain variables from the overrides
        and resolve.
        """
        if validator_dict is None:
            validator_dict = self._validator_dict

        for validator in validator_dict.values():
            if isinstance(validator, DictValidator):
                # Usage of protected variables in other validators is fine. The reason to keep them
                # protected is for readability when using them in subscriptions.
                # pylint: disable=protected-access
                self.__recursive_preset_validate(validator._validator_dict)
                # pylint: enable=protected-access

            if isinstance(validator, OverridesStringFormatterValidator):
                self.__validate_override_string_formatter_validator(validator)

    def __merge_parent_preset_dicts_if_present(self, config: ConfigFile):
        parent_presets = set()
        parent_preset_validator = self._validate_key_if_present(
            key="preset", validator=StringValidator
        )
        parent_preset = parent_preset_validator.value if parent_preset_validator else None

        while parent_preset:
            # Make sure the parent preset actually exists
            if parent_preset not in config.presets.keys:
                raise self._validation_exception(
                    f"preset '{parent_preset}' does not exist in the provided config. "
                    f"Available presets: {', '.join(config.presets.keys)}"
                )

            # Make sure we do not hit an infinite loop
            if parent_preset in parent_presets:
                raise self._validation_exception(
                    f"preset loop detected with the preset '{parent_preset}'"
                )

            parent_preset_dict = copy.deepcopy(config.presets.dict[parent_preset])

            parent_presets.add(parent_preset)
            parent_preset = parent_preset_dict.get("preset")

            # Override the parent preset with the contents of this preset
            self._value = mergedeep.merge(
                parent_preset_dict, self._value, strategy=mergedeep.Strategy.REPLACE
            )

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
        self.plugins = self.__validate_and_get_plugins()

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
