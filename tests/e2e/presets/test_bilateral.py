from typing import Dict

import pytest
from expected_transaction_log import assert_transaction_log_matches
from resources import DISABLE_YOUTUBE_TESTS

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def tv_show_by_date_bilateral_dict(output_directory):
    return {
        "preset": [
            "Jellyfin TV Show by Date",
        ],
        "format": "worst[ext=mp4]",
        "match_filters": {"filters": ["title *= Feb.1"]},
        "overrides": {
            "url": "https://www.youtube.com/playlist?list=PLd4Q7G88JqoekF0b30NYQcOTnTiIe9Ali",
            "tv_show_directory": output_directory,
        },
        "nfo_tags": {
            "tags": {
                "subscription_has_download_archive": "{subscription_has_download_archive}",
                "download_index": "{download_index}",
            }
        },
    }


@pytest.fixture
def tv_show_collection_bilateral_dict(output_directory):
    return {
        "preset": [
            "Jellyfin TV Show Collection",
        ],
        "format": "worst[ext=mp4]",
        "match_filters": {"filters": ["title *= Feb.1"]},
        "overrides": {
            "s01_url": "https://www.youtube.com/playlist?list=PLd4Q7G88JqoekF0b30NYQcOTnTiIe9Ali",
            "s01_name": "bilateral test",
            "tv_show_directory": output_directory,
        },
        "nfo_tags": {
            "tags": {
                "subscription_has_download_archive": "{subscription_has_download_archive}",
                "download_index": "{download_index}",
            }
        },
    }


@pytest.mark.skipif(DISABLE_YOUTUBE_TESTS, reason="YouTube tests cannot run in GH")
class TestBilateral:

    def test_tv_show_by_date_downloads_bilateral(
        self,
        tv_show_by_date_bilateral_dict: Dict,
        output_directory: str,
        default_config: ConfigFile,
    ):
        playlist_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="bilateral_test",
            preset_dict=tv_show_by_date_bilateral_dict,
        )

        transaction_log = playlist_subscription.download(dry_run=False)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist_bilateral_p1.txt",
        )

        # Now that one vid is downloaded, attempt to download all and see if bilateral
        # logic kicks in
        del tv_show_by_date_bilateral_dict["match_filters"]
        playlist_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="bilateral_test",
            preset_dict=tv_show_by_date_bilateral_dict,
        )
        transaction_log = playlist_subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist_bilateral_p2.txt",
        )

    def test_tv_show_collection_downloads_bilateral(
        self,
        tv_show_collection_bilateral_dict: Dict,
        output_directory: str,
        default_config: ConfigFile,
    ):
        playlist_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="bilateral_test",
            preset_dict=tv_show_collection_bilateral_dict,
        )

        transaction_log = playlist_subscription.download(dry_run=False)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist_bilateral_collection_p1.txt",
        )

        # Now that one vid is downloaded, attempt to download all and see if bilateral
        # logic kicks in
        del tv_show_collection_bilateral_dict["match_filters"]
        playlist_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="bilateral_test",
            preset_dict=tv_show_collection_bilateral_dict,
        )
        transaction_log = playlist_subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist_bilateral_collection_p2.txt",
        )
