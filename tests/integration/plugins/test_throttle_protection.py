import re
from typing import Dict

import pytest
from conftest import assert_logs

from ytdl_sub.plugins.throttle_protection import logger as throttle_protection_logger
from ytdl_sub.script.functions.print_functions import logger as script_print_logger
from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import StringFormattingVariableNotFoundException


@pytest.fixture
def throttle_subscription_dict(output_directory) -> Dict:
    return {
        "preset": [
            "Kodi Music Videos",
        ],
        "overrides": {
            "url": "https://your.name.here",
            "music_video_directory": output_directory,
            "bool_false_variable": "{ %bool(False) }",
            "empty_string_variable": "",
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
            "subscription_download_probability": 1.0,
        },
    }


class TestThrottleProtectionPlugin:
    def test_sleeps_log(
        self,
        config,
        subscription_name,
        throttle_subscription_dict,
        output_directory,
        mock_download_collection_entries,
    ):
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=throttle_subscription_dict,
        )

        with (
            mock_download_collection_entries(
                is_youtube_channel=False, num_urls=1, is_extracted_audio=False
            ),
            assert_logs(
                logger=throttle_protection_logger,
                expected_message="Sleeping between downloads for 0.01 seconds",
                log_level="info",
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
                log_level="info",
                expected_occurrences=1,
            ),
        ):
            _ = subscription.download(dry_run=False)

    @pytest.mark.parametrize(
        "disable_value",
        [
            "",
            False,
            "{bool_false_variable}",
            "{empty_string_variable}",
        ],
    )
    def test_disabled(
        self,
        config,
        subscription_name,
        throttle_subscription_dict,
        output_directory,
        mock_download_collection_entries,
        disable_value,
    ):
        throttle_subscription_dict["overrides"]["enable_throttle_protection"] = disable_value
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=throttle_subscription_dict,
        )

        with (
            mock_download_collection_entries(
                is_youtube_channel=False, num_urls=1, is_extracted_audio=False
            ),
            assert_logs(
                logger=throttle_protection_logger,
                expected_message="Sleeping between downloads for %0.2f seconds",
                log_level="info",
                expected_occurrences=0,
            ),
        ):
            _ = subscription.download(dry_run=False)

    def test_max_downloads(
        self,
        config,
        subscription_name,
        throttle_subscription_dict,
        output_directory,
        mock_download_collection_entries,
    ):
        throttle_subscription_dict["throttle_protection"] = {
            "max_downloads_per_subscription": {"max": 0}
        }
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=throttle_subscription_dict,
        )

        with (
            mock_download_collection_entries(
                is_youtube_channel=False, num_urls=1, is_extracted_audio=False, is_dry_run=True
            ),
            assert_logs(
                logger=throttle_protection_logger,
                expected_message="Reached subscription max downloads of %d",
                log_level="info",
                expected_occurrences=1,
            ),
        ):
            transaction_log = subscription.download(dry_run=True)

        assert transaction_log.is_empty

    def test_subscription_proba(
        self,
        config,
        subscription_name,
        throttle_subscription_dict,
        output_directory,
        mock_download_collection_entries,
    ):
        throttle_subscription_dict["throttle_protection"] = {
            "subscription_download_probability": 0.0
        }
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=throttle_subscription_dict,
        )

        with (
            mock_download_collection_entries(
                is_youtube_channel=False, num_urls=1, is_extracted_audio=False, is_dry_run=True
            ),
            assert_logs(
                logger=throttle_protection_logger,
                expected_message="Subscription download probability of",
                log_level="info",
                expected_occurrences=1,
            ),
        ):
            transaction_log = subscription.download(dry_run=True)

        assert transaction_log.is_empty


class TestResolutionAssert:
    @pytest.mark.parametrize(
        "disable_value",
        [
            "",
            False,
            "{bool_false_variable}",
            "{empty_string_variable}",
        ],
    )
    def test_disabled(
        self,
        config,
        subscription_name,
        throttle_subscription_dict,
        output_directory,
        mock_download_collection_entries,
        disable_value,
    ):
        throttle_subscription_dict["overrides"]["enable_resolution_assert"] = disable_value

        with assert_logs(
            logger=script_print_logger,
            expected_message="Resolution assert is disabled. Use at your own risk!",
            log_level="info",
            expected_occurrences=1,
        ):
            _ = Subscription.from_dict(
                config=config,
                preset_name=subscription_name,
                preset_dict=throttle_subscription_dict,
            )

    @pytest.mark.parametrize(
        "width, height",
        [
            (0, 0),  # missing
            (361, 361),  # min value
        ],
    )
    def test_runs_successfully(
        self,
        config,
        subscription_name,
        throttle_subscription_dict,
        output_directory,
        mock_download_collection_entries,
        width,
        height,
    ):
        with assert_logs(
            logger=script_print_logger,
            expected_message=(
                "Resolution assert is enabled, will fail on low-quality video downloads and presume throttle. "
                "Disable using the override variable `enable_resolution_assert: False`"
            ),
            log_level="info",
            expected_occurrences=1,
        ):
            subscription = Subscription.from_dict(
                config=config,
                preset_name=subscription_name,
                preset_dict=throttle_subscription_dict,
            )

        with (
            mock_download_collection_entries(
                is_youtube_channel=False,
                num_urls=1,
                is_extracted_audio=False,
                is_dry_run=True,
                mock_entry_kwargs={"height": height, "width": width},
            ),
        ):
            _ = subscription.download(dry_run=True)

    def test_fails_low_resolution(
        self,
        config,
        subscription_name,
        throttle_subscription_dict,
        output_directory,
        mock_download_collection_entries,
    ):
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=throttle_subscription_dict,
        )

        expected_message = (
            "Entry Mock Entry 20-3 downloaded at a low resolution (640x360), "
            "you've probably been throttled. "
            "Stopping further downloads, wait a few hours and try again. "
            "Disable using the override variable `enable_resolution_assert: False`"
        )

        with (
            mock_download_collection_entries(
                is_youtube_channel=False,
                num_urls=1,
                is_extracted_audio=False,
                is_dry_run=True,
                mock_entry_kwargs={"height": 360, "width": 640},
            ),
            pytest.raises(UserThrownRuntimeError, match=re.escape(expected_message)),
        ):
            _ = subscription.download(dry_run=True)

    def test_sleep_per_download_supports_entry_variables(
        self,
        config,
        subscription_name,
        throttle_subscription_dict,
        output_directory,
        mock_download_collection_entries,
    ):
        throttle_subscription_dict["throttle_protection"]["sleep_per_download_s"] = {
            "min": "{%mul(3.14, duration)}",
            "max": "{%mul(3.14, duration)}",
        }

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=throttle_subscription_dict,
        )

        with (
            mock_download_collection_entries(
                is_youtube_channel=False,
                num_urls=1,
                is_extracted_audio=False,
                mock_entry_kwargs={"duration": 1},
            ),
            assert_logs(
                logger=throttle_protection_logger,
                expected_message="Sleeping between downloads for 3.14 seconds",
                log_level="info",
                expected_occurrences=4,
            ),
        ):
            _ = subscription.download(dry_run=False)

    def test_sleep_per_subscription_does_not_support_entry_variables(
        self,
        config,
        subscription_name,
        throttle_subscription_dict,
        output_directory,
        mock_download_collection_entries,
    ):
        throttle_subscription_dict["throttle_protection"]["sleep_per_subscription_s"] = {
            "min": "{%mul(3.14, duration)}",
            "max": "{%mul(3.14, duration)}",
        }

        with pytest.raises(StringFormattingVariableNotFoundException):
            _ = Subscription.from_dict(
                config=config,
                preset_name=subscription_name,
                preset_dict=throttle_subscription_dict,
            )
