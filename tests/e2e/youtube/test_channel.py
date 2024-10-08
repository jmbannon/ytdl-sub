from typing import Callable
from typing import Dict

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches
from resources import DISABLE_YOUTUBE_TESTS

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def channel_preset_dict(output_directory):
    return {
        "preset": [
            "TV Show Full Archive",
        ],
        "format": "worst[ext=mp4]",  # download the worst format so it is fast
        "ytdl_options": {
            "max_views": 100000,  # do not download the popular PJ concert
        },
        "subtitles": {
            "subtitles_name": "{episode_file_path}.{lang}.{subtitles_ext}",
            "allow_auto_generated_subtitles": True,
        },
        "nfo_tags": {
            "tags": {
                "playlist_index": "{playlist_index}",
                "playlist_count": "{playlist_count}",
            }
        },
        "output_directory_nfo_tags": {
            "tags": {
                "source_uploader": "{playlist_uploader}",
            }
        },
        "overrides": {
            "url": "https://youtube.com/channel/UCcRSMoQqXc_JrBZRHDFGbqA",
            "tv_show_name": "Project / Zombie",
            "tv_show_directory": output_directory,
        },
    }


@pytest.mark.skipif(DISABLE_YOUTUBE_TESTS, reason="YouTube tests cannot run in GH")
class TestChannel:
    """
    Downloads my old minecraft youtube channel. Ensure the above files exist and have the
    expected md5 file hashes.
    """

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_full_channel_download(
        self,
        tv_show_config,
        channel_preset_dict,
        output_directory,
        dry_run,
    ):
        full_channel_subscription = Subscription.from_dict(
            config=tv_show_config, preset_name="pz", preset_dict=channel_preset_dict
        )
        transaction_log = full_channel_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_channel_full.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="youtube/test_channel_full.json",
        )

    def test_full_channel_existing_archive_downloads_nothing(
        self,
        pz_channel_mock_downloaded_with_archive_factory: Callable,
        tv_show_config: ConfigFile,
        channel_preset_dict: Dict,
    ):
        subscription_name = "pz"
        tv_show_name = channel_preset_dict["overrides"]["tv_show_name"]
        archive_file_name = f".ytdl-sub-{subscription_name}-download-archive.json"

        pz_channel_mock_downloaded_with_archive_factory(
            tv_show_name=tv_show_name, archive_file_name=archive_file_name
        )

        full_channel_subscription = Subscription.from_dict(
            config=tv_show_config, preset_name=subscription_name, preset_dict=channel_preset_dict
        )
        transaction_log = full_channel_subscription.download(dry_run=True)
        assert transaction_log.is_empty

    def test_full_channel_existing_archive_keep_max_files(
        self,
        pz_channel_mock_downloaded_with_archive_factory: Callable,
        tv_show_config: ConfigFile,
        channel_preset_dict: Dict,
        output_directory: str,
    ):
        subscription_name = "pz"
        channel_preset_dict["preset"].append("Only Recent")
        channel_preset_dict["overrides"]["only_recent_date_range"] = "10years"
        channel_preset_dict["overrides"]["only_recent_max_files"] = 1

        full_channel_subscription = Subscription.from_dict(
            config=tv_show_config, preset_name=subscription_name, preset_dict=channel_preset_dict
        )
        tv_show_name = channel_preset_dict["overrides"]["tv_show_name"]
        archive_file_name = f".ytdl-sub-{subscription_name}-download-archive.json"

        pz_channel_mock_downloaded_with_archive_factory(
            tv_show_name=tv_show_name, archive_file_name=archive_file_name
        )

        transaction_log = full_channel_subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_channel_full_keep_max_files.txt",
        )
