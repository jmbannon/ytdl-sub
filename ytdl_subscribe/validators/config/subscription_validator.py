from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import yaml
from mergedeep import mergedeep

from ytdl_subscribe.subscriptions.soundcloud import SoundcloudSubscription
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.subscriptions.youtube import YoutubeSubscription
from ytdl_subscribe.utils.enums import SubscriptionSourceName
from ytdl_subscribe.validators.config.config_validator import ConfigValidator
from ytdl_subscribe.validators.config.preset_validator import PresetValidator
from ytdl_subscribe.validators.exceptions import ValidationException


class SubscriptionValidator(PresetValidator):
    """
    A Subscription is a preset but overrides it with specific values
    """

    required_fields = {"preset"}
    optional_fields = {"overrides"}.union(
        PresetValidator.required_fields, PresetValidator.optional_fields
    )

    def __init__(self, config: ConfigValidator, name: str, value: Any):
        super().__init__(name, value)
        self.config = config
        self.overrides: Optional[Dict] = None

    def validate(self) -> "SubscriptionValidator":
        # If a preset is present, update the
        preset_name = self.get("preset")
        available_presets = sorted(list(self.config.presets.keys()))
        if preset_name not in available_presets:
            raise ValidationException(
                f"'{self.name}.preset' does not exist in the provided config. "
                f"Available presets: {', '.join(available_presets)}"
            )

        self.overrides = self.get("overrides", {})

        # A little hacky, we will override the preset with the contents of this subscription, then validate it
        self.value = mergedeep.merge(
            self.config.presets[preset_name].value,
            self.value,
            strategy=mergedeep.Strategy.REPLACE,
        )

        _ = super().validate()
        return self

    def to_subscription(self) -> Subscription:
        subscription_class = None
        if self.subscription_source_name == SubscriptionSourceName.SOUNDCLOUD:
            subscription_class = SoundcloudSubscription
        elif self.subscription_source_name == SubscriptionSourceName.YOUTUBE:
            subscription_class = YoutubeSubscription
        else:
            raise ValueError("subscription source class not found")

        return subscription_class(
            name=self.name,
            options=self.get(self.subscription_source_name),
            ytdl_opts=self.get("ytdl_options"),
            post_process=self.get("post_process"),
            overrides=self.get("overrides"),
            output_path=self.get("output_path"),
        )

    @classmethod
    def from_file_path(
        cls, config: ConfigValidator, subscription_path: str
    ) -> List["SubscriptionValidator"]:
        # TODO: Create separate yaml file loader class
        with open(subscription_path, "r", encoding="utf-8") as file:
            subscription_dict = yaml.safe_load(file)

        subscriptions: List["SubscriptionValidator"] = []
        for subscription_key, subscription_object in subscription_dict.items():
            subscriptions.append(
                SubscriptionValidator(
                    config=config, name=subscription_key, value=subscription_object
                ).validate()
            )

        return subscriptions
