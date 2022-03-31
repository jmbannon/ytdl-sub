from typing import Any
from typing import Optional

from ytdl_subscribe.enums import SubscriptionSourceName
from ytdl_subscribe.validators.config.sources import PresetSource
from ytdl_subscribe.validators.config.sources import SoundcloudSource
from ytdl_subscribe.validators.config.sources import YoutubeSource
from ytdl_subscribe.validators.exceptions import ValidationException
from ytdl_subscribe.validators.native.object_validator import ObjectValidator


class Preset(ObjectValidator):
    required_fields = {"post_process"}
    optional_fields = {"ytdl_options", *SubscriptionSourceName.all()}
    allow_extra_fields = False

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        self.subscription_source: Optional[PresetSource] = None

    def _validate_subscription_source(self):
        # Make sure we only have a single subscription source
        for object_key, object_value in self.object_items:
            if object_key in SubscriptionSourceName.all() and self.subscription_source:
                raise ValidationException(
                    f"'{self.name}' can only have one of the following sources: {SubscriptionSourceName.pretty_all()}"
                )

            if object_key == SubscriptionSourceName.SOUNDCLOUD:
                self.subscription_source = SoundcloudSource(
                    name=f"{self.name}{object_key}", value=object_value
                ).validate()
            elif object_key == SubscriptionSourceName.YOUTUBE:
                self.subscription_source = YoutubeSource(
                    name=f"{self.name}{object_key}", value=object_value
                ).validate()

        # If subscription source was not set, error
        if not self.subscription_source:
            raise ValidationException(
                f"'{self.name} must have one of the following sources: {SubscriptionSourceName.pretty_all()}"
            )

    def validate(self) -> "Preset":
        super().validate()
        self._validate_subscription_source()
        return self
