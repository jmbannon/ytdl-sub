import pytest
import yaml
from resources import file_fixture_path

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def repro_preset_dict(output_directory):
    with open(file_fixture_path("repro.yaml"), "r", encoding="utf-8") as yaml_file:
        yaml_dict = yaml.safe_load(yaml_file)
    out = yaml_dict["presets"]["subs"]
    del out["preset"]
    out["output_options"]["output_directory"] = output_directory
    return out


@pytest.mark.skipif(False, reason="Always skip repro, for local testing only")
class TestReproduce:
    def test_single_video_download(
        self,
        default_config,
        repro_preset_dict,
        output_directory,
    ):
        single_video_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="repro",
            preset_dict=repro_preset_dict,
        )

        transaction_log = single_video_subscription.download(dry_run=False)
        assert not transaction_log.is_empty
