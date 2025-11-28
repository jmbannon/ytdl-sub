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

    def test_multi_url(self, default_config):
        num_seasons = 40
        num_urls_per_season = 11

        overrides = {
            "tv_show_directory": "abc",
        }
        for season_num in range(1, num_seasons + 1):
            overrides[f"s{season_num:02d}_name"] = f"The Season {season_num}"
            overrides[f"s{season_num:02d}_url"] = [
                f"youtube.com/playlist?url_{season_num}_{i}" for i in range(num_urls_per_season)
            ]

        sub = Subscription.from_dict(
            config=default_config,
            preset_name="test",
            preset_dict={"preset": "Jellyfin TV Show Collection", "overrides": overrides},
        )

        assert len(sub.downloader_options.urls.list) == 40 * 11 * 2
        url_list = sub.downloader_options.urls.list
        itr = 0

        # loop twice for bilateral
        for i in range(2):
            for season_num in range(1, num_seasons + 1):
                for i in range(num_urls_per_season):
                    url = sub.overrides.apply_formatter(
                        url_list[itr].url,
                        function_overrides={
                            # mock so bilateral url gets enabled
                            "subscription_has_download_archive": "True"
                        },
                    )
                    variables = url_list[itr].variables.dict
                    assert url == f"youtube.com/playlist?url_{season_num}_{i}"
                    assert (
                        sub.overrides.apply_formatter(variables["collection_season_number"])
                        == f"{season_num}"
                    )
                    assert (
                        sub.overrides.apply_formatter(variables["collection_season_name"])
                        == f"The Season {season_num}"
                    )

                    itr += 1
