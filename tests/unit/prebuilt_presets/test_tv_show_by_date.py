import re

import pytest
import yaml

from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError
from ytdl_sub.subscriptions.subscription import Subscription


class TestTvShowByDatePreset:

    def test_s01_error_thrown(self, default_config):
        with pytest.raises(
            UserThrownRuntimeError,
            match=re.escape(
                "Provided `s01_url` or `s01_name` variable to TV Show by Date preset when it "
                "expects `url`. Perhaps you meant to use the `TV Show Collection` preset?"
            ),
        ):
            _ = Subscription.from_dict(
                config=default_config,
                preset_name="test",
                preset_dict={
                    "preset": "Jellyfin TV Show by Date",
                    "overrides": {"tv_show_directory": "abc", "s01_url": "test"},
                },
            )

    def test_backward_compatibility_single_download(self, default_config):
        a = yaml.safe_load(
            Subscription.from_dict(
                config=default_config,
                preset_name="a",
                preset_dict={
                    "preset": "Jellyfin TV Show by Date",
                    "overrides": {"tv_show_directory": "abc", "url": "test_1"},
                },
            ).resolved_yaml()
        )

        b = yaml.safe_load(
            Subscription.from_dict(
                config=default_config,
                preset_name="a",
                preset_dict={
                    "preset": "Jellyfin TV Show by Date",
                    "overrides": {"tv_show_directory": "abc", "subscription_value": "test_1"},
                },
            ).resolved_yaml()
        )

        assert a["download"] == b["download"]

    def test_backward_compatibility_multi_download(self, default_config):
        a = yaml.safe_load(
            Subscription.from_dict(
                config=default_config,
                preset_name="a",
                preset_dict={
                    "preset": "Jellyfin TV Show by Date",
                    "overrides": {"tv_show_directory": "abc", "url": "test_1", "url2": "test_2"},
                },
            ).resolved_yaml()
        )

        b = yaml.safe_load(
            Subscription.from_dict(
                config=default_config,
                preset_name="a",
                preset_dict={
                    "preset": "Jellyfin TV Show by Date",
                    "overrides": {
                        "tv_show_directory": "abc",
                        "subscription_array": ["test_1", "test_2"],
                    },
                },
            ).resolved_yaml()
        )

        c = yaml.safe_load(
            Subscription.from_dict(
                config=default_config,
                preset_name="a",
                preset_dict={
                    "preset": "Jellyfin TV Show by Date",
                    "overrides": {"tv_show_directory": "abc", "urls": ["test_1", "test_2"]},
                },
            ).resolved_yaml()
        )

        assert a["download"] == b["download"]
        assert a["download"] == c["download"]
