import re

import pytest

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
