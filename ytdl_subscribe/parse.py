import yaml
import time
from getpass import getpass

from mergedeep import mergedeep

from ytdl_subscribe.subscriptions import Subscription

from ytdl_subscribe.enums import YAMLSection


def _set_config_variables(config):
    Subscription.WORKING_DIRECTORY = config.get("working_directory", "")
    Subscription.USERNAME = config.get("ytdl_username")
    if Subscription.USERNAME:
        print(f"Enter password for '{Subscription.USERNAME}': ")
        time.sleep(0.2)
        Subscription.PASSWORD = getpass()


def parse_subscriptions(subscription_yaml_path):
    with open(subscription_yaml_path, "r") as f:
        yaml_dict = yaml.safe_load(f)

    config = yaml_dict[YAMLSection.CONFIG_KEY]
    _set_config_variables(config)

    presets = yaml_dict[YAMLSection.PRESET_KEY]

    subscriptions = []
    for name, subscription in yaml_dict[YAMLSection.SUBSCRIPTIONS_KEY].items():
        preset = {}
        if subscription.get("preset") in presets:
            preset = presets[subscription["preset"]]
        subscription = mergedeep.merge({}, preset, subscription)
        subscriptions.append(Subscription.from_dict(name, subscription))

    return subscriptions
