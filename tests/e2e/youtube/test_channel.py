import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def channel_preset_dict(output_directory):
    return {
        "preset": [
            "jellyfin_tv_show_url",
            "season_by_year__episode_by_month_day",
        ],
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
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
