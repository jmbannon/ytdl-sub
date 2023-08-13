import re
from typing import Dict
from unittest.mock import patch

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.plugins.nfo_tags import NfoTagsOptions
from ytdl_sub.subscriptions.subscription import FILE_SUBSCRIPTION_VALUE_KEY
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException


@pytest.fixture
def preset_file(youtube_video: Dict, output_options: Dict):
    with patch("ytdl_sub.subscriptions.subscription.load_yaml") as mock_load_yaml:
        mock_load_yaml.return_value = {
            "__preset__": {
                "download": youtube_video,
                "output_options": output_options,
                "nfo_tags": {
                    "tags": {"key-3": "file_preset"},
                },
                "overrides": {"test_override": "original"},
            },
            "__value__": "test_override",
            "test_preset": {
                "preset": "parent_preset_3",
                "nfo_tags": {
                    "tags": {"key-4": "test_preset"},
                },
            },
        }
        yield


@pytest.fixture
def preset_file_with_value(youtube_video: Dict, output_options: Dict):
    with patch("ytdl_sub.subscriptions.subscription.load_yaml") as mock_load_yaml:
        mock_load_yaml.return_value = {
            "__preset__": {
                "preset": "parent_preset_3",
                "download": youtube_video,
                "output_options": output_options,
                "nfo_tags": {
                    "tags": {"key-3": "file_preset"},
                },
                "overrides": {"test_override": "original"},
            },
            "__value__": "test_override",
            "test_value": "is_overwritten",
        }
        yield


@pytest.fixture
def preset_file_invalid_value():
    with patch("ytdl_sub.subscriptions.subscription.load_yaml") as mock_load_yaml:
        mock_load_yaml.return_value = {
            "__value__": {"should be": "string"},
        }
        yield


@pytest.fixture
def preset_file_subscription_using_value_when_not_defined():
    with patch("ytdl_sub.subscriptions.subscription.load_yaml") as mock_load_yaml:
        mock_load_yaml.return_value = {"sub_name": "single value, __value__ not defined"}
        yield


@pytest.fixture
def preset_file_subscription_with_invalid_form():
    with patch("ytdl_sub.subscriptions.subscription.load_yaml") as mock_load_yaml:
        mock_load_yaml.return_value = {"sub_name": 4332}
        yield


@pytest.mark.usefixtures(preset_file.__name__)
def test_subscription_file_preset_applies(config_file: ConfigFile):
    subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 1

    # Test __preset__ worked correctly
    preset_sub = subs[0]
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


@pytest.mark.usefixtures(preset_file_with_value.__name__)
def test_subscription_file_value_applies(config_file: ConfigFile):
    subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
    assert len(subs) == 1

    # Test __value__ worked correctly
    value_sub = subs[0]
    assert value_sub.overrides.dict_with_format_strings.get("test_override") == "is_overwritten"


@pytest.mark.usefixtures(preset_file_invalid_value.__name__)
def test_subscription_file_bad_value(config_file: ConfigFile):
    with pytest.raises(
        ValidationException,
        match=re.escape(
            f"Using {FILE_SUBSCRIPTION_VALUE_KEY} in a subscription"
            f"must be a string that corresponds to an override variable"
        ),
    ):
        _ = Subscription.from_file_path(config=config_file, subscription_path="mocked")


@pytest.mark.usefixtures(preset_file_subscription_using_value_when_not_defined.__name__)
def test_subscription_file_using_value_when_not_defined(config_file: ConfigFile):
    with pytest.raises(
        ValidationException,
        match=re.escape(
            f"Subscription sub_name is a string, but "
            f"{FILE_SUBSCRIPTION_VALUE_KEY} is not set to an override variable"
        ),
    ):
        _ = Subscription.from_file_path(config=config_file, subscription_path="mocked")


@pytest.mark.usefixtures(preset_file_subscription_with_invalid_form.__name__)
def test_subscription_file_invalid_form(config_file: ConfigFile):
    with pytest.raises(
        ValidationException,
        match=re.escape(f"Subscription sub_name should be in the form of a preset"),
    ):
        _ = Subscription.from_file_path(config=config_file, subscription_path="mocked")
