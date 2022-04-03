from typing import Any
from typing import List

import yaml
from mergedeep import mergedeep

from ytdl_subscribe.subscriptions.soundcloud import SoundcloudSubscription
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.subscriptions.youtube import YoutubeSubscription
from ytdl_subscribe.utils.enums import SubscriptionSourceName
from ytdl_subscribe.validators.base.dict_validator import DictValidator
from ytdl_subscribe.validators.base.dict_validator import DictWithExtraFieldsValidator
from ytdl_subscribe.validators.base.string_validator import StringValidator
from ytdl_subscribe.validators.config.config_validator import ConfigValidator
from ytdl_subscribe.validators.config.preset_validator import PresetValidator


class SubscriptionValidator(DictValidator):
    """
    A Subscription is a preset but overrides it with specific values
    """

    required_fields = {"preset"}
    optional_fields = PresetValidator.required_fields.union(
        PresetValidator.optional_fields
    )

    def __init__(self, config: ConfigValidator, name: str, value: Any):
        super().__init__(name, value)
        self.config = config
        self.overrides = self.validate_dict_value(
            dict_value_name="overrides",
            validator=DictWithExtraFieldsValidator,
            default={},
        )

        preset_name = self.validate_dict_value(
            dict_value_name="preset",
            validator=StringValidator,
        ).value

        available_presets = self.config.presets.object_keys
        if preset_name not in available_presets:
            raise self._validation_exception(
                f"'preset '{preset_name}' does not exist in the provided config. "
                f"Available presets: {', '.join(available_presets)}"
            )

        # A little hacky, we will override the preset with the contents of this subscription, then validate it
        preset_dict = mergedeep.merge(
            self.config.presets.dict[preset_name],
            self.dict,
            strategy=mergedeep.Strategy.REPLACE,
        )
        del preset_dict["preset"]

        self.preset = PresetValidator(
            name=self.name,
            value=preset_dict,
        )

    def to_subscription(self) -> Subscription:
        if self.preset.subscription_source_name == SubscriptionSourceName.SOUNDCLOUD:
            subscription_class = SoundcloudSubscription
        elif self.preset.subscription_source_name == SubscriptionSourceName.YOUTUBE:
            subscription_class = YoutubeSubscription
        else:
            raise ValueError("subscription source class not found")

        return subscription_class(
            name=self.name,
            options=self.preset.get(self.preset.subscription_source_name),
            ytdl_opts=self.preset.get("ytdl_options"),
            post_process=self.preset.get("post_process"),
            overrides=self.preset.get("overrides"),
            output_path=self.preset.get("output_path"),
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
                )
            )

        return subscriptions
