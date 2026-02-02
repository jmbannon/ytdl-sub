from pathlib import Path

import pytest
import yaml
from resources import expected_json

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.validators.variable_validation import ResolutionLevel
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.file_path import FilePathTruncater


def _ensure_resolved_yaml(
    sub: Subscription, output_directory: str, preset_type: str, resolution_level: int
) -> None:
    output_yaml = sub.resolved_yaml(resolution_level=resolution_level)
    out = yaml.safe_load(output_yaml)

    expected_out_filename = (
        f"{preset_type}/inspect_sub_{ResolutionLevel.name_of(resolution_level)}.json"
    )
    expected_out = expected_json(out, expected_out_filename)

    if resolution_level > ResolutionLevel.ORIGINAL:
        output_path = Path(output_directory)
        if "tv_show_directory" in expected_out["overrides"]:
            output_path = output_path / sub.name

        expected_out["output_options"]["output_directory"] = FilePathTruncater.to_native_filepath(
            str(output_path)
        )

    if "tv_show_directory" in expected_out["overrides"]:
        expected_out["overrides"]["tv_show_directory"] = output_directory
    if "music_directory" in expected_out["overrides"]:
        expected_out["overrides"]["music_directory"] = output_directory
    if "music_video_directory" in expected_out["overrides"]:
        expected_out["overrides"]["music_video_directory"] = output_directory

    assert out == expected_out


@pytest.mark.parametrize("resolution_level", ResolutionLevel.all())
class TestResolution:

    def test_resolution_tv_show(
        self,
        resolution_level: int,
        default_config: ConfigFile,
        tv_show_subscriptions_path: Path,
        output_directory: str,
    ):
        _ensure_resolved_yaml(
            sub=Subscription.from_file_path(
                config=default_config, subscription_path=tv_show_subscriptions_path
            )[0],
            output_directory=output_directory,
            preset_type="tv_show",
            resolution_level=resolution_level,
        )

    def test_resolution_music(
        self,
        resolution_level: int,
        default_config: ConfigFile,
        music_subscriptions_path: Path,
        output_directory: str,
    ):
        _ensure_resolved_yaml(
            sub=Subscription.from_file_path(
                config=default_config, subscription_path=music_subscriptions_path
            )[0],
            output_directory=output_directory,
            preset_type="music",
            resolution_level=resolution_level,
        )

    def test_resolution_music_video(
        self,
        resolution_level: int,
        default_config: ConfigFile,
        music_video_subscription_path: Path,
        output_directory: str,
    ):
        _ensure_resolved_yaml(
            sub=Subscription.from_file_path(
                config=default_config, subscription_path=music_video_subscription_path
            )[0],
            output_directory=output_directory,
            preset_type="music_video",
            resolution_level=resolution_level,
        )
