from unittest.mock import patch

import pytest
from conftest import assert_debug_log
from e2e.expected_download import assert_expected_downloads
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.retry import logger as retry_logger


@pytest.fixture
def channel_preset_dict(output_directory):
    return {
        "preset": "yt_channel_as_tv",
        "youtube": {"channel_url": "https://youtube.com/channel/UCcRSMoQqXc_JrBZRHDFGbqA"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
            "max_views": 100000,  # do not download the popular PJ concert
            "break_on_reject": False,  # do not break from max views
        },
        "subtitles": {
            "subtitles_name": "{episode_name}.{lang}.{subtitles_ext}",
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
                "source_uploader": "{source_uploader}",
            }
        },
        "overrides": {"tv_show_name": "Project / Zombie"},
    }


class TestChannelAsKodiTvShow:
    """
    Downloads my old minecraft youtube channel. Ensure the above files exist and have the
    expected md5 file hashes.
    """

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_full_channel_download(
        self,
        channel_as_tv_show_config,
        channel_preset_dict,
        output_directory,
        dry_run,
    ):
        full_channel_subscription = Subscription.from_dict(
            config=channel_as_tv_show_config, preset_name="pz", preset_dict=channel_preset_dict
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
