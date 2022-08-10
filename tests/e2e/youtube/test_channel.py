import copy
from typing import Dict

import mergedeep
import pytest
from conftest import assert_debug_log
from e2e.expected_download import assert_expected_downloads
from e2e.expected_transaction_log import assert_transaction_log_matches

import ytdl_sub.downloaders.downloader
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def subscription_name():
    return "pz"


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
        "overrides": {"tv_show_name": "Project / Zombie"},
    }


@pytest.fixture
def channel_subscription_generator(channel_as_tv_show_config, subscription_name):
    def _channel_subscription_generator(preset_dict: Dict):
        return Subscription.from_dict(
            config=channel_as_tv_show_config, preset_name=subscription_name, preset_dict=preset_dict
        )

    return _channel_subscription_generator


####################################################################################################
# RECENT CHANNEL FIXTURES
@pytest.fixture
def recent_channel_preset_dict(channel_preset_dict):
    # TODO: remove this hack by using a different channel
    channel_preset_dict = copy.deepcopy(channel_preset_dict)
    del channel_preset_dict["ytdl_options"]["break_on_reject"]
    return mergedeep.merge(
        channel_preset_dict,
        {
            "preset": "yt_channel_as_tv__recent",
            "youtube": {"after": "20150101"},
        },
    )


####################################################################################################
# ROLLING RECENT CHANNEL FIXTURES
@pytest.fixture
def rolling_recent_channel_preset_dict(recent_channel_preset_dict):
    recent_channel_preset_dict = copy.deepcopy(recent_channel_preset_dict)
    return mergedeep.merge(
        recent_channel_preset_dict,
        {
            "preset": "yt_channel_as_tv__only_recent",
            "output_options": {"keep_files_after": "20181101"},
        },
    )


class TestChannelAsKodiTvShow:
    """
    Downloads my old minecraft youtube channel. Ensure the above files exist and have the
    expected md5 file hashes.
    """

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_full_channel_download(
        self,
        channel_subscription_generator,
        channel_preset_dict,
        output_directory,
        dry_run,
    ):
        full_channel_subscription = channel_subscription_generator(preset_dict=channel_preset_dict)
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

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_recent_channel_download(
        self,
        channel_subscription_generator,
        recent_channel_preset_dict,
        output_directory,
        dry_run,
    ):
        recent_channel_subscription = channel_subscription_generator(
            preset_dict=recent_channel_preset_dict
        )

        transaction_log = recent_channel_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_channel_recent.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="youtube/test_channel_recent.json",
        )
        if not dry_run:
            # try downloading again, ensure nothing more was downloaded
            with assert_debug_log(
                logger=ytdl_sub.downloaders.downloader.download_logger,
                expected_message="ExistingVideoReached, stopping additional downloads",
            ):
                transaction_log = recent_channel_subscription.download()
                assert_transaction_log_matches(
                    output_directory=output_directory,
                    transaction_log=transaction_log,
                    transaction_log_summary_file_name=(
                        "youtube/test_channel_no_additional_downloads.txt"
                    ),
                )
                assert_expected_downloads(
                    output_directory=output_directory,
                    dry_run=dry_run,
                    expected_download_summary_file_name="youtube/test_channel_recent.json",
                )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_recent_channel_download__no_vids_in_range(
        self,
        channel_subscription_generator,
        recent_channel_preset_dict,
        output_directory,
        dry_run,
    ):
        recent_channel_preset_dict["youtube"]["after"] = "21000101"

        recent_channel_no_vids_in_range_subscription = channel_subscription_generator(
            preset_dict=recent_channel_preset_dict
        )
        # Run twice, ensure nothing changes between runs
        for _ in range(2):
            transaction_log = recent_channel_no_vids_in_range_subscription.download(dry_run=dry_run)
            assert_transaction_log_matches(
                output_directory=output_directory,
                transaction_log=transaction_log,
                transaction_log_summary_file_name="youtube/test_channel_no_additional_downloads.txt",
            )
            assert_expected_downloads(
                output_directory=output_directory,
                dry_run=dry_run,
                expected_download_summary_file_name="youtube/test_channel_no_additional_downloads.json",
            )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_rolling_recent_channel_download(
        self,
        channel_subscription_generator,
        recent_channel_preset_dict,
        rolling_recent_channel_preset_dict,
        output_directory,
        dry_run,
    ):
        recent_channel_subscription = channel_subscription_generator(
            preset_dict=recent_channel_preset_dict
        )
        rolling_recent_channel_subscription = channel_subscription_generator(
            preset_dict=rolling_recent_channel_preset_dict
        )

        # First, download recent vids. Always download since we want to test dry-run
        # on the rolling recent portion.
        with assert_debug_log(
            logger=ytdl_sub.downloaders.downloader.download_logger,
            expected_message="RejectedVideoReached, stopping additional downloads",
        ):
            transaction_log = recent_channel_subscription.download(dry_run=False)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_channel_recent.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name="youtube/test_channel_recent.json",
        )

        # Then, download the rolling recent vids subscription. This should remove one of the
        # two videos
        with assert_debug_log(
            logger=ytdl_sub.downloaders.downloader.download_logger,
            expected_message="ExistingVideoReached, stopping additional downloads",
        ):
            transaction_log = rolling_recent_channel_subscription.download(dry_run=dry_run)

        expected_downloads_summary = (
            "youtube/test_channel_recent.json"
            if dry_run
            else "youtube/test_channel_rolling_recent.json"
        )

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_channel_rolling_recent.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name=expected_downloads_summary,
        )

        # Invoke the rolling download again, ensure downloading stopped early from it already
        # existing
        if not dry_run:
            with assert_debug_log(
                logger=ytdl_sub.downloaders.downloader.download_logger,
                expected_message="ExistingVideoReached, stopping additional downloads",
            ):
                transaction_log = rolling_recent_channel_subscription.download()

            assert_transaction_log_matches(
                output_directory=output_directory,
                transaction_log=transaction_log,
                transaction_log_summary_file_name="youtube/test_channel_no_additional_downloads.txt",
            )
            assert_expected_downloads(
                output_directory=output_directory,
                dry_run=False,
                expected_download_summary_file_name=expected_downloads_summary,
            )
