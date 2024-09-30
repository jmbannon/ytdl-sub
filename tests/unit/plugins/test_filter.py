from typing import Any
from typing import Dict

import mergedeep
import pytest
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def regex_subscription_dict_base(output_directory):
    return {
        "preset": "Jellyfin Music Videos",
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        "format": "best[height<=480]",  # download the worst format so it is fast
        "filter_include": ["{%not(%is_null(description_website))}"],
        "overrides": {
            "in_regex_default": "in regex default",
            "url": "https://your.name.here",
            "upload_capture": """{
                %regex_capture_many_with_defaults(
                    upload_date_standardized,
                    ["([0-9]+)-([0-9]+)-27"],
                    ["First", %concat("Second containing ", in_regex_default)]
                )
            }""",
            "upload_captured_year": "{%array_at(upload_capture, 1)}",
            "upload_captured_month": "{%array_at(upload_capture, 2)}",
            "description_capture": """{
                %regex_capture_many_with_defaults(
                    description,
                    ["The (.*)"],
                    [null]
                )
            }""",
            "description_website": "{%array_at(description_capture, 1)}",
        },
    }


@pytest.fixture
def regex_subscription_dict(regex_subscription_dict_base, output_directory):
    return mergedeep.merge(
        regex_subscription_dict_base,
        {
            "nfo_tags": {
                "tags": {
                    "title_cap_1": "{title_type}",
                    "title_cap_1_sanitized": "{title_type_sanitized}",
                    "title_cap_2": "{title_date}",
                    "desc_cap": "{description_website}",
                    "upload_date_both_caps": "{upload_captured_year} and {upload_captured_month}",
                    "override_with_capture_variable": "{contains_regex_default}",
                    "override_with_capture_variable_sanitized": "{contains_regex_sanitized_default}",
                }
            },
            "filter_exclude": ["{%is_null(title_type)}"],
            "overrides": {
                "title_capture_list": """{
                    %regex_capture_many_with_defaults(
                        title,
                        [ "should not cap (.+) - (.+)", "Mock Entry (.*)-(.*)" ],
                        [ null, null ]
                    )
                }""",
                "title_type": "{%array_at(title_capture_list, 1)}",
                "title_date": "{%array_at(title_capture_list, 2)}",
                "contains_regex_default": "contains {title_type}",
                "contains_regex_sanitized_default": "contains {title_type_sanitized}",
            },
        },
    )


@pytest.fixture
def regex_subscription_dict_exclude(regex_subscription_dict_base, output_directory):
    return mergedeep.merge(
        regex_subscription_dict_base,
        {
            "filter_exclude": [
                """{
                    %regex_search_any(
                        title,
                        [ "should not cap", "Mock Entry 20-.*" ]
                    )
                }"""
            ]
        },
    )


@pytest.fixture
def playlist_subscription(
    config: ConfigFile, subscription_name: str, regex_subscription_dict: Dict[str, Any]
):
    return Subscription.from_dict(
        config=config,
        preset_name=subscription_name,
        preset_dict=regex_subscription_dict,
    )


@pytest.fixture
def playlist_subscription_exclude(
    config: ConfigFile, subscription_name: str, regex_subscription_dict_exclude: Dict[str, Any]
) -> Subscription:
    return Subscription.from_dict(
        config=config,
        preset_name=subscription_name,
        preset_dict=regex_subscription_dict_exclude,
    )


class TestFilter:
    def test_filter_regex_success(
        self, mock_download_collection_entries, playlist_subscription, output_directory
    ):
        with mock_download_collection_entries(
            is_youtube_channel=False, num_urls=1, is_extracted_audio=False, is_dry_run=True
        ):
            transaction_log = playlist_subscription.download(dry_run=True)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/filter/test_regex.txt",
        )

    def test_filter_regex_excludes_success(
        self, mock_download_collection_entries, playlist_subscription_exclude, output_directory
    ):
        # Should only contain the march video
        with mock_download_collection_entries(
            is_youtube_channel=False, num_urls=1, is_extracted_audio=False, is_dry_run=True
        ):
            transaction_log = playlist_subscription_exclude.download(dry_run=True)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/filter/test_regex_exclude.txt",
        )
