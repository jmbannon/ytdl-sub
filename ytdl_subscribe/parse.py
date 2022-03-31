from typing import Optional

import yaml
from mergedeep import mergedeep

from ytdl_subscribe.enums import SubscriptionSourceName
from ytdl_subscribe.enums import YAMLSection
from ytdl_subscribe.subscriptions.soundcloud import SoundcloudSubscription
from ytdl_subscribe.subscriptions.subscription import Subscription
from ytdl_subscribe.subscriptions.youtube import YoutubeSubscription
from ytdl_subscribe.validators.config.config import Config


def _set_config_variables(config):
    Subscription.WORKING_DIRECTORY = config.get("working_directory", "")


def read_config_file(config_path: str) -> Config:
    with open(config_path, "r", encoding="utf-8") as file:
        config_dict = yaml.safe_load(file)

    return Config(name="config", value=config_dict).validate()


def parse_subscriptions_file(subscription_yaml_path, set_config_variables=True):
    """
    Reads and parses a subscription yaml from its path.
    TODO: trafaret the dict for validation

    Parameters
    ----------
    subscription_yaml_path: str
        File path
    set_config_variables: bool
        Whether to set global config variables

    Returns
    -------
    dict
        The subscription yaml after safe_load
    """
    with open(subscription_yaml_path, "r") as f:
        yaml_dict = yaml.safe_load(f)

    config = yaml_dict[YAMLSection.CONFIG_KEY]

    if set_config_variables:
        _set_config_variables(config)

    return yaml_dict


def parse_presets(yaml_dict):
    """
    Parses presets from a subscription yaml dict

    Parameters
    ----------
    yaml_dict: dict
        Subscription YAML dict

    Returns
    -------
    dict
        Presets
    """
    presets = yaml_dict[YAMLSection.PRESET_KEY]
    return presets


def parse_subscriptions(yaml_dict: dict, presets: dict, subscriptions: Optional[list]):
    """
    Parses config from a subscription yaml dict

    Parameters
    ----------
    yaml_dict: dict
    presets: dict
    subscriptions: list[str] or None
        If present, only parse these config

    Returns
    -------
    list[Subscription]
    """
    parsed_subscriptions = []

    # Parse all config even if all are not used for validation's sake
    for name, subscription in yaml_dict[YAMLSection.SUBSCRIPTIONS_KEY].items():
        preset = {}
        if subscription.get("preset") in presets:
            preset = presets[subscription["preset"]]
        subscription = mergedeep.merge({}, preset, subscription)

        if SubscriptionSourceName.SOUNDCLOUD in subscription:
            subscription_source = SubscriptionSourceName.SOUNDCLOUD
            subscription_class = SoundcloudSubscription
        elif SubscriptionSourceName.YOUTUBE in subscription:
            subscription_source = SubscriptionSourceName.YOUTUBE
            subscription_class = YoutubeSubscription
        else:
            raise ValueError("dne")

        parsed_subscriptions.append(
            subscription_class(
                name=name,
                options=subscription[subscription_source],
                ytdl_opts=subscription["ytdl_opts"],
                post_process=subscription["post_process"],
                overrides=subscription["overrides"],
                output_path=subscription["output_path"],
            )
        )

    # Filter config if present
    if subscriptions:
        parsed_subscriptions = [
            sub for sub in parsed_subscriptions if sub.name in subscriptions
        ]

    return parsed_subscriptions
