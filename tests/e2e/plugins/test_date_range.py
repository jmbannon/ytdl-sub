import copy

import mergedeep
import pytest
from conftest import assert_logs
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches
from resources import DISABLE_YOUTUBE_TESTS

from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def recent_preset_dict(output_directory):
    return {
        "preset": "TV Show Full Archive",
        "date_range": {"after": "20150101"},
        "format": "worst[ext=mp4]",  # download the worst format so it is fast
        "ytdl_options": {
            "max_views": 100000,  # do not download the popular PJ concert
        },
        "overrides": {
            "url": "https://youtube.com/channel/UCcRSMoQqXc_JrBZRHDFGbqA",
            "tv_show_name": "Project / Zombie",
            "tv_show_directory": output_directory,
        },
    }


@pytest.fixture
def rolling_recent_channel_preset_dict(recent_preset_dict):
    preset_dict = copy.deepcopy(recent_preset_dict)
    return mergedeep.merge(
        preset_dict,
        {
            "output_options": {"keep_files_after": "20181101"},
        },
    )


@pytest.mark.skipif(DISABLE_YOUTUBE_TESTS, reason="YouTube tests cannot run in GH")
class TestDateRange:
    @pytest.mark.parametrize("dry_run", [True, False])
    @pytest.mark.parametrize("date_range_breaks", [True, False])
    def test_recent_channel_download(
        self,
        recent_preset_dict,
        tv_show_config,
        output_directory,
        dry_run: bool,
        date_range_breaks: bool,
    ):
        recent_preset_dict["date_range"]["breaks"] = date_range_breaks
        recent_channel_subscription = Subscription.from_dict(
            config=tv_show_config,
            preset_name="recent",
            preset_dict=recent_preset_dict,
        )

        with assert_logs(
            logger=YTDLP.logger,
            expected_message="RejectedVideoReached, stopping additional downloads",
            log_level="debug",
            expected_occurrences=1 if date_range_breaks else 0,
        ):
            transaction_log = recent_channel_subscription.download(dry_run=dry_run)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/date_range/test_channel_recent.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/date_range/test_channel_recent.json",
        )
        if not dry_run:
            # try downloading again, ensure nothing more was downloaded
            with assert_logs(
                logger=YTDLP.logger,
                expected_message="ExistingVideoReached, stopping additional downloads",
                log_level="debug",
            ):
                transaction_log = recent_channel_subscription.download()
                assert_transaction_log_matches(
                    output_directory=output_directory,
                    transaction_log=transaction_log,
                    transaction_log_summary_file_name=("plugins/date_range/no_downloads.txt"),
                )
                assert_expected_downloads(
                    output_directory=output_directory,
                    dry_run=dry_run,
                    expected_download_summary_file_name="plugins/date_range/test_channel_recent.json",
                )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_recent_channel_download__no_vids_in_range(
        self,
        tv_show_config,
        recent_preset_dict,
        output_directory,
        dry_run,
    ):
        recent_preset_dict["date_range"]["after"] = "21000101"

        recent_channel_no_vids_in_range_subscription = Subscription.from_dict(
            config=tv_show_config,
            preset_name="recent",
            preset_dict=recent_preset_dict,
        )

        # run once to initialize all output directory files
        _ = recent_channel_no_vids_in_range_subscription.download(dry_run=False)

        # Run again, ensure no downloads
        transaction_log = recent_channel_no_vids_in_range_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/date_range/no_downloads.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name="plugins/date_range/no_downloads.json",
        )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_rolling_recent_channel_download(
        self,
        tv_show_config,
        recent_preset_dict,
        rolling_recent_channel_preset_dict,
        output_directory,
        dry_run,
    ):
        recent_channel_subscription = Subscription.from_dict(
            config=tv_show_config,
            preset_name="recent",
            preset_dict=recent_preset_dict,
        )
        rolling_recent_channel_subscription = Subscription.from_dict(
            config=tv_show_config,
            preset_name="recent",
            preset_dict=rolling_recent_channel_preset_dict,
        )

        # First, download recent vids. Always download since we want to test dry-run
        # on the rolling recent portion.
        with assert_logs(
            logger=YTDLP.logger,
            expected_message="RejectedVideoReached, stopping additional downloads",
            log_level="debug",
        ):
            transaction_log = recent_channel_subscription.download(dry_run=False)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/date_range/test_channel_recent.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name="plugins/date_range/test_channel_recent.json",
        )

        # Then, download the rolling recent vids subscription. This should remove one of the
        # two videos
        with assert_logs(
            logger=YTDLP.logger,
            expected_message="ExistingVideoReached, stopping additional downloads",
            log_level="debug",
        ):
            transaction_log = rolling_recent_channel_subscription.download(dry_run=dry_run)

        expected_downloads_summary = (
            "plugins/date_range/test_channel_recent.json"
            if dry_run
            else "plugins/date_range/test_channel_rolling_recent.json"
        )

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/date_range/test_channel_rolling_recent.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name=expected_downloads_summary,
        )

        # Invoke the rolling download again, ensure downloading stopped early from it already
        # existing
        if not dry_run:
            with assert_logs(
                logger=YTDLP.logger,
                expected_message="ExistingVideoReached, stopping additional downloads",
                log_level="debug",
            ):
                transaction_log = rolling_recent_channel_subscription.download()

            assert_transaction_log_matches(
                output_directory=output_directory,
                transaction_log=transaction_log,
                transaction_log_summary_file_name="plugins/date_range/no_downloads.txt",
            )
            assert_expected_downloads(
                output_directory=output_directory,
                dry_run=False,
                expected_download_summary_file_name=expected_downloads_summary,
            )
