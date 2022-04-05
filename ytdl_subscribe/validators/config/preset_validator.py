from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.config.metadata_options.metadata_options_validator import (
    MetadataOptionsValidator,
)
from ytdl_subscribe.validators.config.output_options.output_options_validator import (
    OutputOptionsValidator,
)
from ytdl_subscribe.validators.config.overrides.overrides_validator import (
    OverridesValidator,
)
from ytdl_subscribe.validators.config.source_options.soundcloud_validators import (
    SoundcloudSourceValidator,
)
from ytdl_subscribe.validators.config.source_options.source_validator import (
    SourceValidator,
)
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubeSourceValidator,
)
from ytdl_subscribe.validators.config.ytdl_options.ytdl_options_validator import (
    YTDLOptionsValidator,
)
from ytdl_subscribe.validators.exceptions import ValidationException

PRESET_SOURCE_VALIDATOR_MAPPING: Dict[str, Type[SourceValidator]] = {
    "soundcloud": SoundcloudSourceValidator,
    "youtube": YoutubeSourceValidator,
}

PRESET_REQUIRED_KEYS = {"output_options"}
PRESET_OPTIONAL_KEYS = {
    "metadata_options",
    "ytdl_options",
    "overrides",
    *PRESET_SOURCE_VALIDATOR_MAPPING.keys(),
}


class PresetValidator(StrictDictValidator):
    _required_keys = PRESET_REQUIRED_KEYS
    _optional_keys = PRESET_OPTIONAL_KEYS

    @property
    def __available_sources(self) -> List[str]:
        return sorted(list(PRESET_SOURCE_VALIDATOR_MAPPING.keys()))

    def __validate_and_get_subscription_source(self) -> SourceValidator:
        subscription_source: Optional[SourceValidator] = None

        for key in self._keys:
            if key in self.__available_sources and subscription_source:
                raise ValidationException(
                    f"'{self._name}' can only have one of the following sources: "
                    f"{', '.join(self.__available_sources)}"
                )

            if key in PRESET_SOURCE_VALIDATOR_MAPPING:
                subscription_source = self._validate_key(
                    key=key, validator=PRESET_SOURCE_VALIDATOR_MAPPING[key]
                )

        # If subscription source was not set, error
        if not subscription_source:
            raise ValidationException(
                f"'{self._name} must have one of the following sources: "
                f"{', '.join(self.__available_sources)}"
            )

        return subscription_source

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)

        self.subscription_source = self.__validate_and_get_subscription_source()

        self.output_options = self._validate_key(
            key="output_options",
            validator=OutputOptionsValidator,
        )
        self.metadata_options = self._validate_key(
            key="metadata_options", validator=MetadataOptionsValidator
        )

        self.ytdl_options = self._validate_key(
            key="ytdl_options", validator=YTDLOptionsValidator, default={}
        )

        self.overrides = self._validate_key(
            key="overrides", validator=OverridesValidator, default={}
        )
