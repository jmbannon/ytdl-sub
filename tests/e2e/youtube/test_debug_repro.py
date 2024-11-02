import json
from typing import Dict

import pytest
import yaml
from resources import file_fixture_path

from ytdl_sub.subscriptions.subscription import Subscription


def debug_yaml_to_preset_dict(debug_subscription_dict: Dict, output_directory: str) -> Dict:
    presets_level = debug_subscription_dict["presets"]
    assert isinstance(presets_level, dict) and len(presets_level) == 1
    subscription = list(presets_level.values())[0]
    del subscription["preset"]
    subscription["output_options"]["output_directory"] = output_directory
    return subscription


@pytest.fixture
def debug_log_rerpo(output_directory):
    with open(file_fixture_path("repro.yaml"), "r", encoding="utf-8") as yaml_file:
        yaml_dict = yaml.safe_load(yaml_file)
    return debug_yaml_to_preset_dict(
        debug_subscription_dict=yaml_dict,
        output_directory=output_directory,
    )


@pytest.fixture
def subscription_yaml_preset(default_config, output_directory):
    subscriptions = Subscription.from_file_path(
        config=default_config, subscription_path=file_fixture_path("repro.yaml")
    )
    subscription_dict = yaml.safe_load(subscriptions[0].as_yaml())
    return debug_yaml_to_preset_dict(
        debug_subscription_dict=subscription_dict,
        output_directory=output_directory,
    )


@pytest.mark.skipif(False, reason="Always skip repro, for local testing only")
class TestReproduce:
    def test_debug_log_repro(
        self,
        default_config,
        repro_preset_dict,
        output_directory,
    ):
        sub = Subscription.from_dict(
            config=default_config,
            preset_name="repro",
            preset_dict=repro_preset_dict,
        )

        transaction_log = sub.download(dry_run=False)
        assert not transaction_log.is_empty

    def test_subscription_yaml_repro(
        self, default_config, subscription_yaml_preset, output_directory
    ):
        sub = Subscription.from_dict(
            config=default_config,
            preset_name="repro",
            preset_dict=subscription_yaml_preset,
        )

        transaction_log = sub.download(dry_run=False)
        assert not transaction_log.is_empty
