import json
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.plugins.nfo_tags import NfoTagsOptions
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException


@contextmanager
def mock_load_yaml(preset_dict: Dict) -> None:
    with patch("ytdl_sub.subscriptions.subscription.load_yaml") as mock_load_yaml:
        mock_load_yaml.return_value = preset_dict
        yield


@pytest.fixture
def preset_with_file_preset(youtube_video: Dict, output_options: Dict):
    return {
        "__preset__": {
            "download": youtube_video,
            "output_options": output_options,
            "nfo_tags": {
                "nfo_name": "eh",
                "nfo_root": "eh",
                "tags": {"key-3": "file_preset"},
            },
            "overrides": {
                "subscription_indent_1": "original_1",
                "subscription_indent_2": "original_2",
                "current_override": "__preset__",
            },
        },
        "test_preset": {
            "preset": "parent_preset_3",
            "nfo_tags": {
                "tags": {"key-4": "test_preset"},
            },
            "overrides": {"current_override": "test_preset"},
        },
    }


@pytest.fixture
def preset_with_subscription_value(preset_with_file_preset: Dict):
    return dict(
        preset_with_file_preset,
        **{
            "test_value": "is_overwritten",
        },
    )


@pytest.fixture
def subscription_with_period_in_name(preset_with_file_preset: Dict):
    return dict(
        preset_with_file_preset,
        **{
            "Mr. Beast": "is_overwritten",
        },
    )


@pytest.fixture
def preset_with_subscription_value_nested_presets(preset_with_subscription_value: Dict):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2": {
                "parent_preset_1": {"test_2_1": "is_2_1_overwritten"},
                "test_1": "is_1_overwritten",
            }
        },
    )


@pytest.fixture
def preset_with_subscription_value_nested_presets_and_indent_variables(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2": {
                "= INDENT_1   ": {
                    "parent_preset_1": {"test_2_1": "is_2_1_overwritten"},
                    "=INDENT_2": {
                        "test_1": "is_1_overwritten",
                    },
                }
            }
        },
    )


@pytest.fixture
def preset_with_subscription_value_nested_presets_and_indent_variables_same_line(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2": {
                "=INDENT_1": {
                    "parent_preset_1": {"test_2_1": "is_2_1_overwritten"},
                    "= INDENT_2  | = INDENT_3   ": {
                        "test_1": "is_1_overwritten",
                    },
                }
            }
        },
    )


@pytest.fixture
def preset_with_subscription_value_nested_presets_and_indent_variables_all_same_line(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2 | =INDENT_1 | parent_preset_1": {
                "test_2_1": "is_2_1_overwritten",
            },
            "parent_preset_2 | =INDENT_1 |= INDENT_2  | = INDENT_3   ": {
                "test_1": "is_1_overwritten",
            },
        },
    )


@pytest.fixture
def preset_with_subscription_list(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2 | parent_preset_1": {
                "test_2_1": ["is_2_1_overwritten", "is_2_1_list_2"]
            },
        },
    )


@pytest.fixture
def preset_with_subscription_overrides_tilda(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2 | parent_preset_1": {
                "~ test_2_1": {
                    "current_override": "test_2_1",
                    "custom_list": [
                        "elem1",
                        "elem2",
                        "elem3",
                    ],
                    "passed_list_elem": "{%contains_any('elem2', custom_list)}",
                }
            },
        },
    )


@pytest.fixture
def preset_with_subscription_overrides_map(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2 | parent_preset_1": {
                "+ test_2_1": {
                    "custom_key": "custom_value",
                    "custom_list": [
                        "elem1",
                        "elem2",
                        "elem3",
                    ],
                    "custom_map": {"custom_map_key": ["custom_map_list_value"]},
                }
            },
        },
    )


@pytest.fixture
def preset_with_subscription_value_nested_presets_and_indent_variables_same_line_old_format_errors(
    preset_with_subscription_value: Dict,
):
    return dict(
        preset_with_subscription_value,
        **{
            "parent_preset_2": {
                "=INDENT_1": {
                    "parent_preset_1": {"test_2_1": "is_2_1_overwritten"},
                    "= INDENT_2  | INDENT_3   ": {
                        "test_1": "is_1_overwritten",
                    },
                }
            }
        },
    )


def test_subscription_file_preset_applies(config_file: ConfigFile, preset_with_file_preset: Dict):
    with mock_load_yaml(preset_dict=preset_with_file_preset):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 1

    # Test __preset__ worked correctly
    preset_sub = subs[0]
    assert preset_sub.name == "test_preset"

    nfo_options: NfoTagsOptions = preset_sub.plugins.get(NfoTagsOptions)
    tags_string_dict = {
        key: formatter[0].format_string for key, formatter in nfo_options.tags.string_tags.items()
    }

    assert tags_string_dict == {
        "key-1": "preset_0",
        "key-2": "preset_2",
        "key-3": "file_preset",
        "key-4": "test_preset",
    }

    overrides = preset_sub.overrides.script
    # preset overrides take precedence over __preset__
    assert overrides.get("current_override").native == "test_preset"


def test_subscription_list(
    config_file: ConfigFile,
    preset_with_subscription_list: Dict,
):
    with mock_load_yaml(preset_dict=preset_with_subscription_list):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 3

    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.script

    assert sub_2_1.get("subscription_name").native == "test_2_1"
    assert sub_2_1.get("subscription_value").native == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_value_1").native == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_value_2").native == "is_2_1_list_2"
    assert (
        sub_2_1.get("current_override").native == "__preset__"
    )  # ensure __preset__ takes precedence


def test_subscription_overrides_tilda(
    config_file: ConfigFile,
    preset_with_subscription_overrides_tilda: Dict,
):
    with mock_load_yaml(preset_dict=preset_with_subscription_overrides_tilda):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 3

    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.script

    assert sub_2_1.get("subscription_name").native == "test_2_1"
    assert sub_2_1.get("current_override").native == "test_2_1"  # tilda sub takes precedence
    assert sub_2_1.get("passed_list_elem").native is True
    assert sub_2_1.get("custom_list").native == ["elem1", "elem2", "elem3"]


def test_subscription_overrides_map(
    config_file: ConfigFile,
    preset_with_subscription_overrides_map: Dict,
):
    with mock_load_yaml(preset_dict=preset_with_subscription_overrides_map):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 3

    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.script

    assert sub_2_1.get("subscription_name").native == "test_2_1"
    assert sub_2_1.get("subscription_map").native == {
        "custom_key": "custom_value",
        "custom_list": [
            "elem1",
            "elem2",
            "elem3",
        ],
        "custom_map": {"custom_map_key": ["custom_map_list_value"]},
    }


def test_subscription_with_period_in_name(
    config_file: ConfigFile,
    subscription_with_period_in_name: Dict,
):
    with mock_load_yaml(preset_dict=subscription_with_period_in_name):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 2

    assert subs[1].name == "Mr. Beast"
    assert subs[1].overrides.script.get("subscription_name").native == "Mr. Beast"


def test_subscription_file_value_applies_from_config_and_nested_and_indent_variables(
    config_file: ConfigFile,
    preset_with_subscription_value_nested_presets_and_indent_variables: Dict,
):
    with mock_load_yaml(
        preset_dict=preset_with_subscription_value_nested_presets_and_indent_variables
    ):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 4

    sub_test_value = [sub for sub in subs if sub.name == "test_value"][0].overrides.script
    sub_1 = [sub for sub in subs if sub.name == "test_1"][0].overrides.script
    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.script

    assert sub_test_value.get("subscription_indent_1").native == "original_1"
    assert sub_test_value.get("subscription_indent_2").native == "original_2"

    assert sub_1.get("subscription_name").native == "test_1"
    assert sub_1.get("subscription_value").native == "is_1_overwritten"
    assert sub_1.get("subscription_indent_1").native == "INDENT_1"
    assert sub_1.get("subscription_indent_2").native == "INDENT_2"
    assert (
        sub_1.get("current_override").native == "__preset__"
    )  # ensure __preset__ takes precedence

    assert sub_2_1.get("subscription_name").native == "test_2_1"
    assert sub_2_1.get("subscription_value").native == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_indent_1").native == "INDENT_1"
    assert sub_2_1.get("subscription_indent_2").native == "original_2"
    assert (
        sub_2_1.get("current_override").native == "__preset__"
    )  # ensure __preset__ takes precedence


@pytest.mark.parametrize("all_same_line", [True, False])
def test_subscription_file_value_applies_from_config_and_nested_and_indent_variables_same_line(
    config_file: ConfigFile,
    preset_with_subscription_value_nested_presets_and_indent_variables_same_line: Dict,
    preset_with_subscription_value_nested_presets_and_indent_variables_all_same_line: Dict,
    all_same_line: bool,
):
    preset_dict = preset_with_subscription_value_nested_presets_and_indent_variables_same_line
    if all_same_line:
        preset_dict = (
            preset_with_subscription_value_nested_presets_and_indent_variables_all_same_line
        )

    with mock_load_yaml(preset_dict=preset_dict):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 4

    sub_test_value = [sub for sub in subs if sub.name == "test_value"][0].overrides.script
    sub_1 = [sub for sub in subs if sub.name == "test_1"][0].overrides.script
    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.script

    assert sub_test_value.get("subscription_indent_1").native == "original_1"
    assert sub_test_value.get("subscription_indent_2").native == "original_2"

    assert sub_1.get("subscription_name").native == "test_1"
    assert sub_1.get("subscription_value").native == "is_1_overwritten"
    assert sub_1.get("subscription_indent_1").native == "INDENT_1"
    assert sub_1.get("subscription_indent_2").native == "INDENT_2"
    assert sub_1.get("subscription_indent_3").native == "INDENT_3"
    # ensure __preset__ takes precedence
    assert sub_1.get("current_override").native == "__preset__"

    assert sub_2_1.get("subscription_name").native == "test_2_1"
    assert sub_2_1.get("subscription_value").native == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_indent_1").native == "INDENT_1"
    assert sub_2_1.get("subscription_indent_2").native == "original_2"
    # ensure __preset__ takes precedence
    assert sub_2_1.get("current_override").native == "__preset__"
    assert "subscription_indent_3" not in sub_2_1.variable_names


def test_subscription_file_value_applies_from_config_and_nested_and_indent_variables_same_line_old_format_errors(
    config_file: ConfigFile,
    preset_with_subscription_value_nested_presets_and_indent_variables_same_line_old_format_errors: Dict,
):
    with (
        mock_load_yaml(
            preset_dict=preset_with_subscription_value_nested_presets_and_indent_variables_same_line_old_format_errors
        ),
        pytest.raises(
            ValidationException,
            match=re.escape(
                "Validation error in parent_preset_2.=INDENT_1: 'INDENT_3' in '= INDENT_2  | INDENT_3' is not a preset name. "
                "To use as a subscription indent value, define it as '= INDENT_3'"
            ),
        ),
    ):
        Subscription.from_file_path(config=config_file, subscription_path="mocked")


def test_subscription_file_using_conflicting_preset_name(config_file: ConfigFile):
    with (
        mock_load_yaml(
            preset_dict={
                "= INDENTS_IN_ERR_MSG ": {"=ANOTHER": {"jellyfin_tv_show_by_date": "single value"}}
            }
        ),
        pytest.raises(
            ValidationException,
            match=re.escape(
                "Validation error in = INDENTS_IN_ERR_MSG .=ANOTHER.jellyfin_tv_show_by_date: "
                "jellyfin_tv_show_by_date conflicts with an existing preset name and cannot be used "
                "as a subscription name"
            ),
        ),
    ):
        _ = Subscription.from_file_path(config=config_file, subscription_path="mocked")


def test_subscription_file_invalid_form(config_file: ConfigFile):
    with (
        mock_load_yaml(preset_dict={"sub_name": 4332}),
        pytest.raises(
            ValidationException,
            match=re.escape(f"Subscription value should either be a string, list, or object"),
        ),
    ):
        _ = Subscription.from_file_path(config=config_file, subscription_path="mocked")


def test_tv_show_subscriptions(config_file: ConfigFile, tv_show_subscriptions_path: Path):
    subs = Subscription.from_file_path(
        config=config_file, subscription_path=tv_show_subscriptions_path
    )

    assert len(subs) == 8
    assert subs[3].name == "Jake Trains"
    jake_train_overrides = subs[3].overrides.script

    assert jake_train_overrides.get("subscription_name").native == "Jake Trains"
    assert (
        jake_train_overrides.get("subscription_value").native
        == "https://www.youtube.com/@JakeTrains"
    )
    assert jake_train_overrides.get("subscription_indent_1").native == "Kids"
    assert jake_train_overrides.get("subscription_indent_2").native == "TV-Y"


def test_advanced_tv_show_subscriptions(
    tv_show_config: ConfigFile, advanced_tv_show_subscriptions_path: Path
):
    subs = Subscription.from_file_path(
        config=tv_show_config, subscription_path=advanced_tv_show_subscriptions_path
    )

    assert len(subs) == 9
    assert subs[3].name == "Jake Trains"
    jake_train_overrides = subs[3].overrides.script

    assert jake_train_overrides.get("subscription_name").native == "Jake Trains"
    assert (
        jake_train_overrides.get("subscription_value").native
        == "https://www.youtube.com/@JakeTrains"
    )
    assert jake_train_overrides.get("subscription_indent_1").native == "Kids"
    assert jake_train_overrides.get("subscription_indent_2").native == "TV-Y"

    assert subs[5].name == "Gardening with Ciscoe"
    overrides = subs[5].overrides

    assert overrides.script.get("subscription_name").native == "Gardening with Ciscoe"
    assert (
        overrides.apply_formatter(overrides.dict["url"])
        == "https://www.youtube.com/@gardeningwithciscoe4430"
    )
    assert (
        overrides.apply_formatter(overrides.dict["url2"])
        == "https://www.youtube.com/playlist?list=PLi8V8UemxeG6lo5if5H5g5EbsteELcb0_"
    )

    assert overrides.apply_formatter(overrides.dict["subscription_array"]) == json.dumps(
        [
            "https://www.youtube.com/@gardeningwithciscoe4430",
            "https://www.youtube.com/playlist?list=PLi8V8UemxeG6lo5if5H5g5EbsteELcb0_",
            "https://www.youtube.com/playlist?list=PLsJlQSR-KjmaQqqJ9jq18cF6XXXAR4kyn",
            "https://www.youtube.com/watch?v=2vq-vPubS5I",
        ]
    )


def test_music_subscriptions(default_config: ConfigFile, music_subscriptions_path: Path):
    subs = Subscription.from_file_path(
        config=default_config, subscription_path=music_subscriptions_path
    )

    assert len(subs) == 14
    assert subs[2].name == "Stan Getz"
    monk = subs[2].overrides.script

    assert monk.get("subscription_name").native == "Stan Getz"
    assert (
        monk.get("subscription_value").native
        == "https://www.youtube.com/@stangetzofficial/releases"
    )
    assert monk.get("subscription_indent_1").native == "Jazz"


def test_music_video_subscriptions(default_config: ConfigFile, music_video_subscription_path: Path):
    subs = Subscription.from_file_path(
        config=default_config, subscription_path=music_video_subscription_path
    )

    assert len(subs) == 4
    assert subs[1].name == "Michael Jackson"
    jackson = subs[1].overrides.script

    assert jackson.get("subscription_name").native == "Michael Jackson"
    assert (
        jackson.get("subscription_value").native
        == "https://www.youtube.com/playlist?list=OLAK5uy_mnY03zP6abNWH929q2XhGzWD_2uKJ_n8E"
    )
    assert jackson.get("subscription_indent_1").native == "Pop"
    assert (
        jackson.get("url").native
        == "https://www.youtube.com/playlist?list=OLAK5uy_mnY03zP6abNWH929q2XhGzWD_2uKJ_n8E"
    )

    assert subs[3].name == "Guns N' Roses"
    gnr = subs[3].overrides.script

    assert gnr.get("subscription_name").native == "Guns N' Roses"
    assert (
        gnr.get("url").native
        == "https://www.youtube.com/playlist?list=PLOTK54q5K4INNXaHKtmXYr6J7CajWjqeJ"
    )
    assert gnr.get("subscription_indent_1").native == "Rock"
    assert gnr.get("url2").native == "https://www.youtube.com/watch?v=OldpIhHPsbs"


def test_default_docker_config_and_subscriptions():
    default_config = ConfigFile.from_file_path("docker/root/defaults/config.yaml")
    default_subs = Subscription.from_file_path(
        config=default_config, subscription_path=Path("docker/root/defaults/subscriptions.yaml")
    )
    assert len(default_subs) == 15
