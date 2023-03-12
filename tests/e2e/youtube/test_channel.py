from pathlib import Path

import pytest
from yt_dlp.utils import sanitize_filename

from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def channel_preset_dict(output_directory):
    return {
        "preset": [
            "tv_show",
            "include_info_json",
        ],
        "ytdl_options": {
            "format": "worst[ext=mp4]",  # download the worst format so it is fast
            "max_views": 100000,  # do not download the popular PJ concert
            "break_on_reject": False,  # do not break from max views
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


class TestChannel:
    """
    Downloads my old minecraft youtube channel. Ensure the above files exist and have the
    expected md5 file hashes.
    """

    @pytest.mark.parametrize("dry_run", [True, False])
    @pytest.mark.parametrize("reformat", [True, False])
    def test_full_channel_download_and_reformat(
        self,
        channel_as_tv_show_config,
        music_video_config,
        channel_preset_dict,
        output_directory,
        reformat_directory,
        dry_run,
        reformat,
    ):
        full_channel_subscription = Subscription.from_dict(
            config=channel_as_tv_show_config, preset_name="pz", preset_dict=channel_preset_dict
        )
        transaction_log = full_channel_subscription.download(dry_run=dry_run and not reformat)
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

        if not reformat:
            return

        reformat_directory = Path(reformat_directory) / sanitize_filename("Project / Zombie")
        full_channel_subscription.reformat(reformat_output_directory=reformat_directory, dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=reformat_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_channel_full.txt",
        )
        assert_expected_downloads(
            output_directory=reformat_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="youtube/test_channel_full.json",
        )

