import pytest
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def filter_subscription_dict(output_directory):
    return {
        "preset": [
            "Plex TV Show by Date",
            "Filter Duration",
        ],
        "overrides": {"url": "https://your.name.here", "tv_show_directory": output_directory},
    }


class TestFilterKeywords:

    def test_no_overrides(
        self,
        config,
        filter_subscription_dict,
        output_directory,
        subscription_name,
        mock_download_collection_entries,
    ):
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=filter_subscription_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=False, num_urls=1, is_dry_run=True
        ):
            transaction_log = subscription.download(dry_run=True)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"integration/prebuilt_presets/filter_keywords_empty.txt",
        )

    @pytest.mark.parametrize("filter_eval, filter_value, filters_all",
        [
            ("min", 10, False),
            ("max", 100, False),
            ("min", 100, True),
            ("max", 10, True),
        ]
    )
    def test_filter_duration(
        self,
        config,
        filter_subscription_dict,
        output_directory,
        subscription_name,
        mock_download_collection_entries,
        filter_eval: str,
        filter_value: int,
        filters_all: bool,
    ):
        filter_subscription_dict["overrides"][f"filter_duration_{filter_eval}_s"] = filter_value
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=filter_subscription_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=False, num_urls=1, is_dry_run=True
        ):
            transaction_log = subscription.download(dry_run=True)

        if filters_all:
            assert transaction_log.is_empty
        else:
            assert_transaction_log_matches(
                output_directory=output_directory,
                transaction_log=transaction_log,
                transaction_log_summary_file_name=f"integration/prebuilt_presets/filter_duration.txt",
            )


    @pytest.mark.parametrize(
        "filter_eval",
        [
            "min",
            "max"
        ],
    )
    def test_error_not_numeric(
        self,
        config,
        filter_subscription_dict,
        output_directory,
        subscription_name,
        mock_download_collection_entries,
        filter_eval,
    ):
        filter_subscription_dict["overrides"][f"filter_duration_{filter_eval}_s"] = "egg"
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=filter_subscription_dict,
        )

        with (
            mock_download_collection_entries(is_youtube_channel=False, num_urls=1, is_dry_run=True),
            pytest.raises(UserThrownRuntimeError, match=f"filter_duration args must be numeric"),
        ):
            _ = subscription.download(dry_run=True)

