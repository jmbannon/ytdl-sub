import copy
from typing import Any
from typing import Dict
from typing import List

import yaml
from mergedeep import mergedeep

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import PRESET_OPTIONAL_KEYS
from ytdl_sub.config.preset import PRESET_REQUIRED_KEYS
from ytdl_sub.config.preset import Preset
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.validators import StringValidator


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

        self.preset = Preset(
            name=f"{self._name}.{preset_name}",
            value=preset_dict,
        )

    def to_subscription(self) -> Subscription:
        """
        Returns
        -------
        The subscription after the config and preset have been validated
        """
        return Subscription(
            name=self._name,
            config_options=self.config.config_options,
            preset_options=self.preset,
        )

    @classmethod
    def from_dict(
        cls, config: ConfigFile, subscription_name: str, subscription_dict: Dict
    ) -> "SubscriptionValidator":
        """
        Parameters
        ----------
        config:
            Validated instance of the config
        subscription_name:
            Name of the subscription
        subscription_dict:
            The subscription config in dict format

        Returns
        -------
        The Subscription validator
        """
        return SubscriptionValidator(config=config, name=subscription_name, value=subscription_dict)

    @classmethod
    def from_file_path(
        cls, config: ConfigFile, subscription_path: str
    ) -> List["SubscriptionValidator"]:
        """
        Parameters
        ----------
        config:
            Validated instance of the config
        subscription_path:
            File path to the subscription yaml file

        Returns
        -------
        List of subscription validators, for each one in the subscription yaml
        """
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
