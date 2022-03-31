from typing import Any
from typing import Optional

from ytdl_subscribe.utils.enums import SubscriptionSourceName
from ytdl_subscribe.validators.base.object_validator import ObjectValidator
from ytdl_subscribe.validators.config.sources.base_source_validator import (
    BaseSourceValidator,
)
from ytdl_subscribe.validators.config.sources.soundcloud_source_validator import (
    SoundcloudSourceValidator,
)
from ytdl_subscribe.validators.config.sources.youtube_source_validator import (
    YoutubeSourceValidator,
)
from ytdl_subscribe.validators.exceptions import ValidationException


class PresetValidator(ObjectValidator):
    required_fields = {"post_process"}
    optional_fields = {"ytdl_options", "output_path", *SubscriptionSourceName.all()}
    allow_extra_fields = False

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.subscription_source: Optional[BaseSourceValidator] = None
        self.subscription_source_name: Optional[str] = None

    def _validate_subscription_source(self):
        # Make sure we only have a single subscription source
        for object_key, object_value in self.object_items:
            if object_key in SubscriptionSourceName.all() and self.subscription_source:
                raise ValidationException(
                    f"'{self.name}' can only have one of the following sources: {SubscriptionSourceName.pretty_all()}"
                )

            if object_key == SubscriptionSourceName.SOUNDCLOUD:
                self.subscription_source_name = SubscriptionSourceName.SOUNDCLOUD
                self.subscription_source = SoundcloudSourceValidator(
                    name=f"{self.name}{object_key}", value=object_value
                ).validate()
            elif object_key == SubscriptionSourceName.YOUTUBE:
                self.subscription_source_name = SubscriptionSourceName.YOUTUBE
                self.subscription_source = YoutubeSourceValidator(
                    name=f"{self.name}{object_key}", value=object_value
                ).validate()

        # If subscription source was not set, error
        if not self.subscription_source:
            raise ValidationException(
                f"'{self.name} must have one of the following sources: {SubscriptionSourceName.pretty_all()}"
            )

    def validate(self) -> "PresetValidator":
        super().validate()
        self._validate_subscription_source()
        return self
