import copy
from typing import Any
from typing import Dict
from typing import List

import yaml
from mergedeep import mergedeep

from ytdl_subscribe.config.config_file import ConfigFile
from ytdl_subscribe.config.preset import PRESET_OPTIONAL_KEYS
from ytdl_subscribe.config.preset import PRESET_REQUIRED_KEYS
from ytdl_subscribe.config.preset import Overrides
from ytdl_subscribe.config.preset import PresetValidator
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.validators.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.validators import StringValidator


class SubscriptionValidator(StrictDictValidator):
    """
    A Subscription is a preset but overrides it with specific values
    """

    _required_keys = {"preset"}
    _optional_keys = PRESET_REQUIRED_KEYS.union(PRESET_OPTIONAL_KEYS)

    def __init__(self, config: ConfigFile, name: str, value: Any):
        super().__init__(name, value)
        self.config = config

        # Ensure the overrides defined here are valid
        _ = self._validate_key(
            key="overrides",
            validator=Overrides,
            default={},
        )

        preset_name = self._validate_key(
            key="preset",
            validator=StringValidator,
        ).value

        if preset_name not in self.config.presets.keys:
            raise self._validation_exception(
                f"preset '{preset_name}' does not exist in the provided config. "
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
        # TODO: Fix this abomination
        return None
        # subscription_class: Optional[Type[Subscription]] = None
        # if isinstance(self.preset.subscription_source, SoundcloudAlbumsAndSinglesDownloadOptions):
        #     subscription_class = SoundcloudAlbumsAndSinglesSubscription
        # elif isinstance(self.preset.subscription_source, YoutubePlaylistDownloaderValidator):
        #     subscription_class = YoutubePlaylistSubscription
        # elif isinstance(self.preset.subscription_source, YoutubeVideoDownloaderValidator):
        #     subscription_class = YoutubeVideoSubscription
        # elif isinstance(self.preset.subscription_source, YoutubeChannelDownloaderValidator):
        #     subscription_class = YoutubeChannelSubscription
        # if subscription_class is None:
        #     raise ValueError("subscription source class not found")
        #
        # return subscription_class(
        #     name=self._name,
        #     config_options=self.config.config_options,
        #     preset_options=self.preset,
        # )

    @classmethod
    def from_dict(
        cls, config: ConfigFile, subscription_name, subscription_dict: Dict
    ) -> "SubscriptionValidator":
        return SubscriptionValidator(config=config, name=subscription_name, value=subscription_dict)

    @classmethod
    def from_file_path(
        cls, config: ConfigFile, subscription_path: str
    ) -> List["SubscriptionValidator"]:
        # TODO: Create separate yaml file loader class
        with open(subscription_path, "r", encoding="utf-8") as file:
            subscription_dict = yaml.safe_load(file)

        subscriptions: List["SubscriptionValidator"] = []
        for subscription_key, subscription_object in subscription_dict.items():
            subscriptions.append(
                SubscriptionValidator.from_dict(
                    config=config,
                    subscription_name=subscription_key,
                    subscription_dict=subscription_object,
                )
            )

        return subscriptions
