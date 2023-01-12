from typing import Dict
from unittest.mock import patch

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.plugins.nfo_tags import NfoTagsOptions
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def preset_file(youtube_video: Dict, output_options: Dict) -> Dict:
    return {
        "__preset__": {
            "download": youtube_video,
            "output_options": output_options,
            "nfo_tags": {
                "tags": {"key-3": "file_preset"},
            },
        },
        "test_preset": {
            "preset": "parent_preset_3",
            "nfo_tags": {
                "tags": {"key-4": "test_preset"},
            },
        },
    }


def test_subscription_file_preset_applies(config_file: ConfigFile, preset_file: Dict):
    with patch("ytdl_sub.subscriptions.subscription.load_yaml") as mock_load_yaml:
        mock_load_yaml.return_value = preset_file

        subs = Subscription.from_file_path(config=config_file, subscription_path="mocked")
        assert len(subs) == 1

        nfo_options: NfoTagsOptions = subs[0].plugins.get(NfoTagsOptions)
        tags_string_dict = {
            key: formatter[0].format_string
            for key, formatter in nfo_options.tags.string_tags.items()
        }

        assert tags_string_dict == {
            "key-1": "preset_0",
            "key-2": "preset_2",
            "key-3": "file_preset",
            "key-4": "test_preset",
        }
