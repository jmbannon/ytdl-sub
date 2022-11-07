import copy
from typing import Dict
from typing import List

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription_download import SubscriptionDownload
from ytdl_sub.utils.yaml import load_yaml
from ytdl_sub.validators.validators import LiteralDictValidator

FILE_PRESET_APPLY_KEY = "__preset__"


class Subscription(SubscriptionDownload):
    @classmethod
    def from_preset(cls, preset: Preset, config: ConfigFile) -> "Subscription":
        """
        Creates a subscription from a preset

        Parameters
        ----------
        preset
            Preset to make the subscription out of
        config
            The config file that should contain this preset

        Returns
        -------
        Initialized subscription
        """
        return cls(
            name=preset.name,
            preset_options=preset,
            config_options=config.config_options,
        )

    @classmethod
    def from_dict(cls, config: ConfigFile, preset_name: str, preset_dict: Dict) -> "Subscription":
        """
        Creates a subscription from a preset dict

        Parameters
        ----------
        config:
            Validated instance of the config
        preset_name:
            Name of the preset
        preset_dict:
            The preset config in dict format

        Returns
        -------
        Initialized subscription
        """
        return cls.from_preset(
            preset=Preset.from_dict(
                config=config,
                preset_name=preset_name,
                preset_dict=preset_dict,
            ),
            config=config,
        )

    @classmethod
    def from_file_path(cls, config: ConfigFile, subscription_path: str) -> List["Subscription"]:
        """
        Loads subscriptions from a file and applies __preset__ to all of them if present.

        Parameters
        ----------
        config:
            Validated instance of the config
        subscription_path:
            File path to the subscription yaml file

        Returns
        -------
        List of subscriptions, for each one in the subscription yaml
        """
        subscriptions: List["Subscription"] = []
        subscription_dict = load_yaml(file_path=subscription_path)

        has_file_preset = FILE_PRESET_APPLY_KEY in subscription_dict

        # If a file preset is present...
        if has_file_preset:
            # Validate it (make sure it is a dict)
            file_preset = LiteralDictValidator(
                name=f"{subscription_path}.{FILE_PRESET_APPLY_KEY}",
                value=subscription_dict[FILE_PRESET_APPLY_KEY],
            )

            # Deep copy the config and add this file preset to its preset list
            config = copy.deepcopy(config)
            config.presets.dict[FILE_PRESET_APPLY_KEY] = file_preset.dict

        for subscription_key, subscription_object in subscription_dict.items():

            # Skip file preset
            if subscription_key == FILE_PRESET_APPLY_KEY:
                continue

            # If it has file_preset, inject it as a parent preset
            if has_file_preset:
                parent_preset = subscription_object.get("preset", [])
                # Preset can be a single string
                if isinstance(parent_preset, str):
                    parent_preset = [parent_preset]

                # If it's not a string or list, it will fail downstream
                if isinstance(parent_preset, list):
                    subscription_object["preset"] = parent_preset + [FILE_PRESET_APPLY_KEY]

            subscriptions.append(
                cls.from_dict(
                    config=config,
                    preset_name=subscription_key,
                    preset_dict=subscription_object,
                )
            )

        return subscriptions
