import pytest
from conftest import assert_logs

from ytdl_sub.plugins.throttle_protection import logger as throttle_protection_logger
from ytdl_sub.subscriptions.subscription import Subscription


class TestThrottleProtectionPlugin:
    def test_sleeps_log(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
    ):
        preset_dict = {
            "preset": [
                "Kodi Music Videos",
            ],
            "overrides": {
                "url": "https://your.name.here",
                "music_video_directory": output_directory,
            },
            "throttle_protection": {
                "sleep_per_download_s": {
                    "min": 0.01,
                    "max": 0.01,
                },
                "sleep_per_subscription_s": {
                    "min": 0.02,
                    "max": 0.02,
                },
            },
        }

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=preset_dict,
        )

        with (
            mock_download_collection_entries(
                is_youtube_channel=False, num_urls=1, is_extracted_audio=False
            ),
            assert_logs(
                logger=throttle_protection_logger,
                expected_message="Sleeping between downloads for %0.2f seconds",
                log_level="debug",
                expected_occurrences=4,
            ),
        ):
            _ = subscription.download(dry_run=False)

        with (
            mock_download_collection_entries(
                is_youtube_channel=False, num_urls=1, is_extracted_audio=False
            ),
            assert_logs(
                logger=throttle_protection_logger,
                expected_message="Sleeping between subscriptions for %0.2f seconds",
                log_level="debug",
                expected_occurrences=1,
            ),
        ):
            _ = subscription.download(dry_run=False)

    @pytest.mark.parametrize(
        "disable_value",
        [
            "",
            False,
            "{tp_bool_string}",
            "{tp_empty_string}",
        ],
    )
    def test_disabled(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        disable_value,
    ):
        preset_dict = {
            "preset": [
                "Kodi Music Videos",
            ],
            "overrides": {
                "url": "https://your.name.here",
                "music_video_directory": output_directory,
                "tp_bool_string": "{ %bool(False) }",
                "tp_empty_string": "",
            },
            "throttle_protection": {
                "enable": disable_value,
                "sleep_per_download_s": {
                    "min": 0.01,
                    "max": 0.01,
                },
                "sleep_per_subscription_s": {
                    "min": 0.02,
                    "max": 0.02,
                },
            },
        }

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=preset_dict,
        )

        with (
            mock_download_collection_entries(
                is_youtube_channel=False, num_urls=1, is_extracted_audio=False
            ),
            assert_logs(
                logger=throttle_protection_logger,
                expected_message="Sleeping between downloads for %0.2f seconds",
                log_level="debug",
                expected_occurrences=0,
            ),
        ):
            _ = subscription.download(dry_run=False)
