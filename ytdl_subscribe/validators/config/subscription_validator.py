import copy
from typing import Any
from typing import List

import yaml
from mergedeep import mergedeep

from ytdl_subscribe.subscriptions.soundcloud import SoundcloudAlbumsAndSinglesSubscription
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.subscriptions.youtube import YoutubePlaylistSubscription
from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.validators import StringValidator
from ytdl_subscribe.validators.config.config_file_validator import ConfigFileValidator
from ytdl_subscribe.validators.config.overrides.overrides_validator import OverridesValidator
from ytdl_subscribe.validators.config.preset_validator import PRESET_OPTIONAL_KEYS
from ytdl_subscribe.validators.config.preset_validator import PRESET_REQUIRED_KEYS
from ytdl_subscribe.validators.config.preset_validator import PresetValidator
from ytdl_subscribe.validators.config.source_options.soundcloud_validators import (
    SoundcloudAlbumsAndSinglesDownloadValidator,
)
from ytdl_subscribe.validators.config.source_options.youtube_validators import (
    YoutubePlaylistDownloadValidator,
)


class SubscriptionValidator(StrictDictValidator):
    """
    A Subscription is a preset but overrides it with specific values
    """

    _required_keys = {"preset"}
    _optional_keys = PRESET_REQUIRED_KEYS.union(PRESET_OPTIONAL_KEYS)

    def __init__(self, config: ConfigFileValidator, name: str, value: Any):
        super().__init__(name, value)
        self.config = config

        # Ensure the overrides defined here are valid
        _ = self._validate_key(
            key="overrides",
            validator=OverridesValidator,
            default={},
        )

        preset_name = self._validate_key(
            key="preset",
            validator=StringValidator,
        ).value

        if preset_name not in self.config.presets.keys:
            raise self._validation_exception(
                f"'preset '{preset_name}' does not exist in the provided config. "
                f"Available presets: {', '.join(self.config.presets.keys)}"
            )

        # A little hacky, we will override the preset with the contents of this subscription,
        # then validate it
        preset_dict = copy.deepcopy(self.config.presets.dict[preset_name])
        preset_dict = mergedeep.merge(preset_dict, self._dict, strategy=mergedeep.Strategy.REPLACE)
        del preset_dict["preset"]

        self.preset = PresetValidator(
            name=f"{self._name}.{preset_name}",
            value=preset_dict,
        )

    def to_subscription(self) -> Subscription:
        if isinstance(self.preset.subscription_source, SoundcloudAlbumsAndSinglesDownloadValidator):
            subscription_class = SoundcloudAlbumsAndSinglesSubscription
        elif isinstance(self.preset.subscription_source, YoutubePlaylistDownloadValidator):
            subscription_class = YoutubePlaylistSubscription
        else:
            raise ValueError("subscription source class not found")

        return subscription_class(
            name=self._name,
            config_options=self.config.config_options,
            preset_options=self.preset,
        )

    @classmethod
    def from_file_path(
        cls, config: ConfigFileValidator, subscription_path: str
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
