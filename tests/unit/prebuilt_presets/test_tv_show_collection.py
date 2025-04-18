import re

import pytest

from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError
from ytdl_sub.subscriptions.subscription import Subscription


class TestTvShowCollectionPreset:

    def test_url_error_thrown(self, default_config):
        with pytest.raises(
            UserThrownRuntimeError,
            match=re.escape(
                "Provided `url` to TV Show Collection preset when it expects `s01_url`. "
                "Perhaps you meant to use the `TV Show by Date` preset?"
            ),
        ):
            _ = Subscription.from_dict(
                config=default_config,
                preset_name="test",
                preset_dict={
                    "preset": "Jellyfin TV Show Collection",
                    "overrides": {"tv_show_directory": "abc", "url": "test"},
                },
            )
