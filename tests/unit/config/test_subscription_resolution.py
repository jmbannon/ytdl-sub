from pathlib import Path

import pytest
import yaml
from resources import expected_json

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.validators.variable_validation import ResolutionLevel
from ytdl_sub.subscriptions.subscription import Subscription


def _ensure_resolved_yaml(sub: Subscription, preset_type: str, resolution_level: int) -> None:
    output_yaml = sub.resolved_yaml(resolution_level=resolution_level)
    out = yaml.safe_load(output_yaml)

    expected_out_filename = (
        f"{preset_type}/inspect_sub_{ResolutionLevel.name_of(resolution_level)}.json"
    )
    assert out == expected_json(out, expected_out_filename)


@pytest.mark.parametrize("resolution_level", ResolutionLevel.all())
def test_resolution_original_tv_show(
    resolution_level: int, config_file: ConfigFile, tv_show_subscriptions_path: Path
):
    _ensure_resolved_yaml(
        sub=Subscription.from_file_path(
            config=config_file, subscription_path=tv_show_subscriptions_path
        )[0],
        preset_type="tv_show",
        resolution_level=resolution_level,
    )
