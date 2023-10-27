import re
from contextlib import contextmanager
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest
from mergedeep import mergedeep

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.plugins.nfo_tags import NfoTagsOptions
from ytdl_sub.subscriptions.subscription import FILE_SUBSCRIPTION_VALUE_KEY
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.yaml import load_yaml


@pytest.fixture
def config_file_with_subscription_value(config_file: ConfigFile):
    config_dict = config_file.as_dict()
    mergedeep.merge(
        config_dict, {"configuration": {"subscription_value": "test_config_subscription_value"}}
    )
    return ConfigFile.from_dict(config_dict)


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
                "test_file_subscription_value": "original",
                "test_config_subscription_value": "original",
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
def preset_with_subscription_file_value(preset_with_subscription_value: Dict):
    return dict(
        preset_with_subscription_value,
        **{
            "__value__": "test_file_subscription_value",
            "test_value": "is_overwritten",
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

    overrides = preset_sub.overrides.dict_with_format_strings
    # preset overrides take precedence over __preset__
    assert overrides.get("current_override") == "test_preset"


def test_subscription_file_value_applies(
    config_file: ConfigFile, preset_with_subscription_file_value: Dict
):
    with mock_load_yaml(preset_dict=preset_with_subscription_file_value):
        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 2

    # Test __value__ worked correctly
    value_sub = subs[1]
    overrides = value_sub.overrides.dict_with_format_strings
    assert value_sub.name == "test_value"

    assert overrides.get("test_file_subscription_value") == "is_overwritten"
    assert overrides.get("test_file_subscription_value")
    assert overrides.get("subscription_value") == "is_overwritten"
    assert overrides.get("current_override") == "__preset__"  # ensure __preset__ takes precedence


def test_subscription_file_value_applies_sub_file_takes_precedence(
    config_file_with_subscription_value: ConfigFile,
    preset_with_subscription_file_value: Dict,
):
    with mock_load_yaml(preset_dict=preset_with_subscription_file_value):
        subs = Subscription.from_file_path(
            config=config_file_with_subscription_value, subscription_path="mocked"
        )
    assert len(subs) == 2

    # Test __value__ worked correctly
    value_sub = subs[1].overrides.dict_with_format_strings
    assert value_sub.get("test_file_subscription_value") == "is_overwritten"
    assert value_sub.get("test_config_subscription_value") == "original"
    assert value_sub.get("subscription_name") == "test_value"
    assert value_sub.get("subscription_value") == "is_overwritten"
    assert value_sub.get("current_override") == "__preset__"  # ensure __preset__ takes precedence


def test_subscription_file_value_applies_from_config(
    config_file_with_subscription_value: ConfigFile, preset_with_subscription_value: Dict
):
    with mock_load_yaml(preset_dict=preset_with_subscription_value):
        subs = Subscription.from_file_path(
            config=config_file_with_subscription_value, subscription_path="mocked"
        )
    assert len(subs) == 2

    # Test __value__ worked correctly from the config
    value_sub = subs[1].overrides.dict_with_format_strings
    assert value_sub.get("test_file_subscription_value") == "original"
    assert value_sub.get("test_config_subscription_value") == "is_overwritten"
    assert value_sub.get("subscription_name") == "test_value"
    assert value_sub.get("subscription_value") == "is_overwritten"
    assert value_sub.get("current_override") == "__preset__"  # ensure __preset__ takes precedence


def test_subscription_file_value_applies_from_config_and_nested(
    config_file_with_subscription_value: ConfigFile,
    preset_with_subscription_value_nested_presets: Dict,
):
    with mock_load_yaml(preset_dict=preset_with_subscription_value_nested_presets):
        subs = Subscription.from_file_path(
            config=config_file_with_subscription_value, subscription_path="mocked"
        )
    assert len(subs) == 4

    # Test __value__ worked correctly from the config
    sub_1 = [sub for sub in subs if sub.name == "test_1"][0].overrides.dict_with_format_strings
    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.dict_with_format_strings

    assert sub_1.get("test_config_subscription_value") == "is_1_overwritten"
    assert sub_1.get("subscription_name") == "test_1"
    assert sub_1.get("subscription_value") == "is_1_overwritten"
    assert sub_1.get("current_override") == "__preset__"  # ensure __preset__ takes precedence

    assert sub_2_1.get("test_config_subscription_value") == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_name") == "test_2_1"
    assert sub_2_1.get("subscription_value") == "is_2_1_overwritten"
    assert sub_2_1.get("current_override") == "__preset__"  # ensure __preset__ takes precedence


def test_subscription_file_value_applies_from_config_and_nested_and_indent_variables(
    config_file_with_subscription_value: ConfigFile,
    preset_with_subscription_value_nested_presets_and_indent_variables: Dict,
):
    with mock_load_yaml(
        preset_dict=preset_with_subscription_value_nested_presets_and_indent_variables
    ):
        subs = Subscription.from_file_path(
            config=config_file_with_subscription_value, subscription_path="mocked"
        )
    assert len(subs) == 4

    # Test __value__ worked correctly from the config
    sub_test_value = [sub for sub in subs if sub.name == "test_value"][
        0
    ].overrides.dict_with_format_strings
    sub_1 = [sub for sub in subs if sub.name == "test_1"][0].overrides.dict_with_format_strings
    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.dict_with_format_strings

    assert sub_test_value.get("subscription_indent_1") == "original_1"
    assert sub_test_value.get("subscription_indent_2") == "original_2"

    assert sub_1.get("test_config_subscription_value") == "is_1_overwritten"
    assert sub_1.get("subscription_name") == "test_1"
    assert sub_1.get("subscription_value") == "is_1_overwritten"
    assert sub_1.get("subscription_indent_1") == "INDENT_1"
    assert sub_1.get("subscription_indent_2") == "INDENT_2"
    assert sub_1.get("current_override") == "__preset__"  # ensure __preset__ takes precedence

    assert sub_2_1.get("test_config_subscription_value") == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_name") == "test_2_1"
    assert sub_2_1.get("subscription_value") == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_indent_1") == "INDENT_1"
    assert sub_2_1.get("subscription_indent_2") == "original_2"
    assert sub_2_1.get("current_override") == "__preset__"  # ensure __preset__ takes precedence


def test_subscription_file_value_applies_from_config_and_nested_and_indent_variables_same_line(
    config_file_with_subscription_value: ConfigFile,
    preset_with_subscription_value_nested_presets_and_indent_variables_same_line: Dict,
):
    with mock_load_yaml(
        preset_dict=preset_with_subscription_value_nested_presets_and_indent_variables_same_line
    ):
        subs = Subscription.from_file_path(
            config=config_file_with_subscription_value, subscription_path="mocked"
        )
    assert len(subs) == 4

    # Test __value__ worked correctly from the config
    sub_test_value = [sub for sub in subs if sub.name == "test_value"][
        0
    ].overrides.dict_with_format_strings
    sub_1 = [sub for sub in subs if sub.name == "test_1"][0].overrides.dict_with_format_strings
    sub_2_1 = [sub for sub in subs if sub.name == "test_2_1"][0].overrides.dict_with_format_strings

    assert sub_test_value.get("subscription_indent_1") == "original_1"
    assert sub_test_value.get("subscription_indent_2") == "original_2"

    assert sub_1.get("test_config_subscription_value") == "is_1_overwritten"
    assert sub_1.get("subscription_name") == "test_1"
    assert sub_1.get("subscription_value") == "is_1_overwritten"
    assert sub_1.get("subscription_indent_1") == "INDENT_1"
    assert sub_1.get("subscription_indent_2") == "INDENT_2"
    assert sub_1.get("subscription_indent_3") == "INDENT_3"
    assert sub_1.get("current_override") == "__preset__"  # ensure __preset__ takes precedence

    assert sub_2_1.get("test_config_subscription_value") == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_name") == "test_2_1"
    assert sub_2_1.get("subscription_value") == "is_2_1_overwritten"
    assert sub_2_1.get("subscription_indent_1") == "INDENT_1"
    assert sub_2_1.get("subscription_indent_2") == "original_2"
    assert sub_2_1.get("current_override") == "__preset__"  # ensure __preset__ takes precedence
    assert "subscription_indent_3" not in sub_2_1


def test_subscription_file_bad_value(config_file: ConfigFile):
    with mock_load_yaml(preset_dict={"__value__": {"should be": "string"}}), pytest.raises(
        ValidationException,
        match=re.escape(
            f"Using {FILE_SUBSCRIPTION_VALUE_KEY} in a subscription"
            f"must be a string that corresponds to an override variable"
        ),
    ):
        _ = Subscription.from_file_path(config=config_file, subscription_path="mocked")


def test_subscription_file_using_conflicting_preset_name(config_file: ConfigFile):
    with mock_load_yaml(
        preset_dict={
            "= INDENTS_IN_ERR_MSG ": {
                "=ANOTHER": {"jellyfin_tv_show_by_date": "single value, __value__ not defined"}
            }
        }
    ), pytest.raises(
        ValidationException,
        match=re.escape(
            "Validation error in = INDENTS_IN_ERR_MSG .=ANOTHER.jellyfin_tv_show_by_date: "
            "jellyfin_tv_show_by_date conflicts with an existing preset name and cannot be used "
            "as a subscription name"
        ),
    ):
        _ = Subscription.from_file_path(config=config_file, subscription_path="mocked")


def test_subscription_file_invalid_form(config_file: ConfigFile):
    with mock_load_yaml(preset_dict={"sub_name": 4332}), pytest.raises(
        ValidationException,
        match=re.escape(f"Validation error in sub_name: should be of type object."),
    ):
        _ = Subscription.from_file_path(config=config_file, subscription_path="mocked")


def test_tv_show_subscriptions(
    channel_as_tv_show_config: ConfigFile, tv_show_subscriptions_path: Path
):
    subs = Subscription.from_file_path(
        config=channel_as_tv_show_config, subscription_path=tv_show_subscriptions_path
    )

    assert len(subs) == 5
    assert subs[2].name == "Jake Trains"
    jake_train_overrides = subs[2].overrides.dict_with_format_strings

    assert jake_train_overrides["subscription_name"] == "Jake Trains"
    assert jake_train_overrides["subscription_value"] == "https://www.youtube.com/@JakeTrains"
    assert jake_train_overrides["subscription_indent_1"] == "Kids"
    assert jake_train_overrides["subscription_indent_2"] == "TV-Y"


def test_music_subscriptions(default_config: ConfigFile, music_subscriptions_path: Path):
    subs = Subscription.from_file_path(
        config=default_config, subscription_path=music_subscriptions_path
    )

    assert len(subs) == 14
    assert subs[2].name == "Stan Getz"
    monk = subs[2].overrides.dict_with_format_strings

    assert monk["subscription_name"] == "Stan Getz"
    assert monk["subscription_value"] == "https://www.youtube.com/@stangetzofficial/releases"
    assert monk["subscription_indent_1"] == "Jazz"


def test_music_video_subscriptions(default_config: ConfigFile, music_video_subscription_path: Path):
    subs = Subscription.from_file_path(
        config=default_config, subscription_path=music_video_subscription_path
    )

    assert len(subs) == 3
    assert subs[1].name == "Michael Jackson"
    monk = subs[1].overrides.dict_with_format_strings

    assert monk["subscription_name"] == "Michael Jackson"
    assert (
        monk["subscription_value"]
        == "https://www.youtube.com/playlist?list=OLAK5uy_mnY03zP6abNWH929q2XhGzWD_2uKJ_n8E"
    )
    assert monk["subscription_indent_1"] == "Pop"
