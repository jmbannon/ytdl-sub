from typing import Dict

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription_download import SubscriptionDownload


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
