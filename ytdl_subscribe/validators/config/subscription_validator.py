from typing import Any
from typing import List

import yaml
from mergedeep import mergedeep

from ytdl_subscribe.subscriptions.soundcloud import (
    SoundcloudAlbumsAndSinglesSubscription,
)
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.subscriptions.youtube import YoutubeSubscription
from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.validators import StringValidator
from ytdl_subscribe.validators.config.config_validator import ConfigValidator
from ytdl_subscribe.validators.config.preset_validator import OverridesValidator
from ytdl_subscribe.validators.config.preset_validator import PresetValidator
from ytdl_subscribe.validators.config.sources.soundcloud_validators import (
    SoundcloudAlbumsAndSinglesDownloadValidator,
)
from ytdl_subscribe.validators.config.sources.youtube_validators import (
    YoutubePlaylistDownloadValidator,
)


class SubscriptionValidator(StrictDictValidator):
    """
    A Subscription is a preset but overrides it with specific values
    """

    required_keys = {"preset"}
    optional_keys = PresetValidator.required_keys.union(PresetValidator.optional_keys)

    def __init__(self, config: ConfigValidator, name: str, value: Any):
        super().__init__(name, value)
        self.config = config

        # Ensure the overrides defined here are valid
        _ = self.validate_key(
            key="overrides",
            validator=OverridesValidator,
            default={},
        )

        preset_name = self.validate_key(
            key="preset",
            validator=StringValidator,
        ).value

        available_presets = self.config.presets.keys
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
            name=f"{self.name}.{preset_name}",
            value=preset_dict,
        )

    def to_subscription(self) -> Subscription:
        if isinstance(
            self.preset.subscription_source.download_strategy,
            SoundcloudAlbumsAndSinglesDownloadValidator,
        ):
            subscription_class = SoundcloudAlbumsAndSinglesSubscription
        elif isinstance(
            self.preset.subscription_source.download_strategy,
            YoutubePlaylistDownloadValidator,
        ):
            subscription_class = YoutubeSubscription
        else:
            raise ValueError("subscription source class not found")

        return subscription_class(
            name=self.name,
            config_options=self.config,
            source_options=self.preset.subscription_source,
            output_options=self.preset.output_options,
            metadata_options=self.preset.metadata_options,
            ytdl_options=self.preset.ytdl_options,
            overrides=self.preset.overrides,
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
