from typing import Any
from typing import Optional

from ytdl_subscribe.utils.enums import SubscriptionSourceName
from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.config.sources.soundcloud_validators import (
    SoundcloudSourceValidator,
)
from ytdl_subscribe.validators.config.sources.source_validator import SourceValidator
from ytdl_subscribe.validators.config.sources.youtube_validators import (
    YoutubeSourceValidator,
)
from ytdl_subscribe.validators.exceptions import ValidationException


class PresetValidator(StrictDictValidator):
    required_keys = {"post_process"}
    optional_keys = {
        "ytdl_options",
        "output_path",
        "overrides",
        *SubscriptionSourceName.all(),
    }

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.subscription_source: Optional[SourceValidator] = None
        self.subscription_source_name: Optional[str] = None

        for key, val in self.dict.items():
            if key in SubscriptionSourceName.all() and self.subscription_source:
                raise ValidationException(
                    f"'{self.name}' can only have one of the following sources: {SubscriptionSourceName.pretty_all()}"
                )

            if key == SubscriptionSourceName.SOUNDCLOUD:
                self.subscription_source_name = SubscriptionSourceName.SOUNDCLOUD
                self.subscription_source = self.validate_key(
                    key=key,
                    validator=SoundcloudSourceValidator,
                )
            elif key == SubscriptionSourceName.YOUTUBE:
                self.subscription_source_name = SubscriptionSourceName.YOUTUBE
                self.subscription_source = self.validate_key(
                    key=key,
                    validator=YoutubeSourceValidator,
                )

        # If subscription source was not set, error
        if not self.subscription_source:
            raise ValidationException(
                f"'{self.name} must have one of the following sources: {SubscriptionSourceName.pretty_all()}"
            )
