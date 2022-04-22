from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from ytdl_subscribe.config.preset_class_mappings import DownloadStrategyMapping
from ytdl_subscribe.config.preset_class_mappings import PluginMapping
from ytdl_subscribe.config.preset_options import OutputOptions
from ytdl_subscribe.config.preset_options import Overrides
from ytdl_subscribe.config.preset_options import YTDLOptions
from ytdl_subscribe.downloaders.downloader import Downloader
from ytdl_subscribe.downloaders.downloader import DownloaderValidator
from ytdl_subscribe.plugins.plugin import Plugin
from ytdl_subscribe.plugins.plugin import PluginOptions
from ytdl_subscribe.utils.exceptions import StringFormattingVariableNotFoundException
from ytdl_subscribe.validators.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_subscribe.validators.validators import DictValidator
from ytdl_subscribe.validators.validators import StringValidator
from ytdl_subscribe.validators.validators import Validator

PRESET_REQUIRED_KEYS = {"output_options"}
PRESET_OPTIONAL_KEYS = {
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
        try:
            return DownloadStrategyMapping.get(
                source=downloader_source, download_strategy=self.download_strategy_name
            )
        except ValueError as value_exc:
            raise self._validation_exception(error_message=value_exc)


class Preset(StrictDictValidator):
    _required_keys = PRESET_REQUIRED_KEYS
    _optional_keys = PRESET_OPTIONAL_KEYS

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

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)

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
