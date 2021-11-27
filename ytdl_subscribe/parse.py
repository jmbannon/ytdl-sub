import yaml

from mergedeep import mergedeep

from ytdl_subscribe.subscriptions.subscription import Subscription

from ytdl_subscribe.enums import YAMLSection


def _set_config_variables(config):
    Subscription.WORKING_DIRECTORY = config.get("working_directory", "")


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


def parse_subscriptions(yaml_dict, presets, subscriptions=None):
    """
    Parses subscriptions from a subscription yaml dict

    Parameters
    ----------
    yaml_dict: dict
    presets: dict
    subscriptions: list of str or None
        If present, only parse these subscriptions

    Returns
    -------
    list of Subscription
    """
    parsed_subscriptions = []

    # Parse all subscriptions even if all are not used for validation's sake
    for name, subscription in yaml_dict[YAMLSection.SUBSCRIPTIONS_KEY].items():
        preset = {}
        if subscription.get("preset") in presets:
            preset = presets[subscription["preset"]]
        subscription = mergedeep.merge({}, preset, subscription)
        parsed_subscriptions.append(Subscription.from_dict(name, subscription))

    # Filter subscriptions if present
    if subscriptions:
        parsed_subscriptions = [
            sub for sub in parsed_subscriptions if sub.name in subscriptions
        ]

    return parsed_subscriptions
