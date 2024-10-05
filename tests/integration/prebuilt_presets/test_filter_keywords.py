import re

import pytest
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException


@pytest.fixture
def filter_subscription_dict(output_directory):
    return {
        "preset": [
            "Plex TV Show by Date",
            "Filter Keywords",
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

    @pytest.mark.parametrize("filter_mode", ["include", "exclude"])
    def test_title(
        self,
        config,
        filter_subscription_dict,
        output_directory,
        subscription_name,
        mock_download_collection_entries,
        filter_mode: str,
    ):
        filter_subscription_dict["overrides"][f"title_{filter_mode}_keywords"] = [
            "not included",
            "MOCK ENTRY 20-3",
        ]
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
            transaction_log_summary_file_name=f"integration/prebuilt_presets/title_filter_keywords_{filter_mode}.txt",
        )

    @pytest.mark.parametrize("filter_mode", ["include", "exclude"])
    def test_description(
        self,
        config,
        filter_subscription_dict,
        output_directory,
        subscription_name,
        mock_download_collection_entries,
        filter_mode: str,
    ):
        filter_subscription_dict["overrides"][f"description_{filter_mode}_keywords"] = [
            "no filter here",
            "description",
        ]
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
            transaction_log_summary_file_name=f"integration/prebuilt_presets/description_filter_keywords_{filter_mode}.txt",
        )

    @pytest.mark.parametrize(
        "keyword_variable",
        [
            "title_include_keywords",
            "title_exclude_keywords",
            "description_include_keywords",
            "description_exclude_keywords",
        ],
    )
    def test_error_not_list_type(
        self,
        config,
        filter_subscription_dict,
        output_directory,
        subscription_name,
        mock_download_collection_entries,
        keyword_variable,
    ):
        filter_subscription_dict["overrides"][keyword_variable] = "not array"
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=filter_subscription_dict,
        )

        with (
            mock_download_collection_entries(is_youtube_channel=False, num_urls=1, is_dry_run=True),
            pytest.raises(UserThrownRuntimeError, match=f"{keyword_variable} must be an array"),
        ):
            _ = subscription.download(dry_run=True)

    @pytest.mark.parametrize(
        "keyword_variable",
        [
            "title_include_keywords",
            "title_exclude_keywords",
            "description_include_keywords",
            "description_exclude_keywords",
        ],
    )
    def test_error_not_string_keyword(
        self,
        config,
        filter_subscription_dict,
        output_directory,
        subscription_name,
        mock_download_collection_entries,
        keyword_variable,
    ):
        filter_subscription_dict["overrides"][keyword_variable] = "{['str', ['nested array not']]}"
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=filter_subscription_dict,
        )

        with (
            mock_download_collection_entries(is_youtube_channel=False, num_urls=1, is_dry_run=True),
            pytest.raises(UserThrownRuntimeError, match="filter keywords must be strings"),
        ):
            _ = subscription.download(dry_run=True)
