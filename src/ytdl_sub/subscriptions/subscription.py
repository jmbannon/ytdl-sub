import copy
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from mergedeep import mergedeep

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription_download import SubscriptionDownload
from ytdl_sub.subscriptions.subscription_validators import SubscriptionValidator
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.yaml import load_yaml
from ytdl_sub.validators.validators import LiteralDictValidator

FILE_PRESET_APPLY_KEY = "__preset__"

logger = Logger.get("subscription")


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
    def from_file_path(
        cls,
        config: ConfigFile,
        subscription_path: str | Path,
        subscription_matches: Optional[List[str]] = None,
        subscription_override_dict: Optional[Dict] = None,
    ) -> List["Subscription"]:
        """
        Loads subscriptions from a file.

        Parameters
        ----------
        config:
            Validated instance of the config
        subscription_path:
            File path to the subscription yaml file
        subscription_matches:
            Optional list, only output subscriptions that match one or more of these values
        subscription_override_dict:
            Optional dict containing overrides to every subscription

        Returns
        -------
        List of subscriptions, for each one in the subscription yaml

        Raises
        ------
        ValidationException
            If subscription file is misconfigured
        """
        subscriptions: List["Subscription"] = []
        subscription_object = load_yaml(file_path=subscription_path)

        has_file_preset = FILE_PRESET_APPLY_KEY in subscription_object

        # If a file preset is present...
        if has_file_preset:
            # Validate it (make sure it is a dict)
            file_preset = LiteralDictValidator(
                name=f"{subscription_path}.{FILE_PRESET_APPLY_KEY}",
                value=subscription_object[FILE_PRESET_APPLY_KEY],
            )

            # Deep copy the config and add this file preset to its preset list
            config = copy.deepcopy(config)
            config.presets.dict[FILE_PRESET_APPLY_KEY] = file_preset.dict

        subscriptions_dict: Dict[str, Any] = {
            key: obj
            for key, obj in subscription_object.items()
            if key not in [FILE_PRESET_APPLY_KEY]
        }

        subscriptions_dicts = SubscriptionValidator(
            name="",
            value=subscriptions_dict,
            config=config,
            presets=[],
            indent_overrides=[],
        ).subscription_dicts(
            global_presets_to_apply=[FILE_PRESET_APPLY_KEY] if has_file_preset else []
        )

        if subscriptions_dicts and subscription_matches:
            logger.info("Filtering subscriptions by name based on --match arguments")
            subscriptions_dicts = {
                subscription_name: subscription_object
                for subscription_name, subscription_object in subscriptions_dicts.items()
                if any(match in subscription_name for match in subscription_matches)
            }

        for subscription_name, subscription_object in subscriptions_dicts.items():

            # Hard-override subscriptions here
            mergedeep.merge(
                subscription_object,
                subscription_override_dict or {},
                strategy=mergedeep.Strategy.ADDITIVE,
            )

            subscriptions.append(
                cls.from_dict(
                    config=config,
                    preset_name=subscription_name,
                    preset_dict=subscription_object,
                )
            )

        return subscriptions
