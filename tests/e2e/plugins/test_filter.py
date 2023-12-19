import copy
import re
from typing import Any
from typing import Dict

import mergedeep
import pytest
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import RegexNoMatchException
from ytdl_sub.utils.exceptions import ValidationException


@pytest.fixture
def regex_subscription_dict_base(output_directory):
    return {
        "preset": "Jellyfin Music Videos",
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        "format": "best[height<=480]",  # download the worst format so it is fast
        "filter_exclude": ["{%is_null(description_website)}"],
        "overrides": {
            "in_regex_default": "in regex default",
            "url": "https://youtube.com/playlist?list=PL5BC0FC26BECA5A35",
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
                    [".*http:\\/\\/(.+).com.*"],
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
                        [ "should not cap (.+) - (.+)", ".*\\[(.+) - (Feb.+)]" ],
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
                        [ "should not cap", ".*Feb.*" ]
                    )
                }"""
            ]
        },
    )


@pytest.fixture
def regex_subscription_dict_match_and_exclude(regex_subscription_dict_base, output_directory):
    return mergedeep.merge(
        regex_subscription_dict_base,
        {
            "regex": {
                # tests that skip_if_match_fails defaults to True
                "from": {
                    "title": {
                        "match": [
                            "should not cap (.+) - (.+)",
                            ".*\\[(.+) - (Feb.+)]",  # should filter out march video
                        ],
                        "capture_group_names": ["title_type", "title_date"],
                        "exclude": [
                            "should not cap",
                            ".*27.*",  # should filter out Feb 27th video
                        ],
                    },
                },
            },
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
            "overrides": {
                "contains_regex_default": "contains {title_type}",
                "contains_regex_sanitized_default": "contains {title_type_sanitized}",
            },
        },
    )


@pytest.fixture
def regex_subscription_dict_match_and_exclude_override_variable(
    regex_subscription_dict_base, output_directory
):
    return mergedeep.merge(
        regex_subscription_dict_base,
        {
            "regex": {
                # tests that skip_if_match_fails defaults to True
                "from": {
                    "override_title": {
                        "exclude": [
                            "should not cap",
                            ".*Feb.*",  # should filter out march video
                        ],
                    },
                    "override_description": {
                        "match": [".*http:\\/\\/(.+).com.*"],
                        "capture_group_names": ["override_description_website"],
                    },
                },
            },
            "overrides": {"override_title": "{title}", "override_description": "{description}"},
        },
    )


@pytest.fixture
def playlist_subscription(default_config, regex_subscription_dict):
    return Subscription.from_dict(
        config=default_config,
        preset_name="regex_capture_playlist_test",
        preset_dict=regex_subscription_dict,
    )


@pytest.fixture
def playlist_subscription_no_match_fails(
    default_config: ConfigFile, regex_subscription_dict: Dict[str, Any]
):
    regex_subscription_dict["overrides"][
        "title_capture_list"
    ] = """{
        %regex_capture_many_required(
            title,
            [ "should not cap (.+) - (.+)", ".*\\[(.+) - (Feb.+)]" ]
        )
    }"""

    return Subscription.from_dict(
        config=default_config,
        preset_name="regex_capture_playlist_test",
        preset_dict=regex_subscription_dict,
    )


@pytest.fixture
def playlist_subscription_exclude(
    default_config: ConfigFile, regex_subscription_dict_exclude: Dict[str, Any]
) -> Subscription:
    return Subscription.from_dict(
        config=default_config,
        preset_name="regex_exclude_playlist_test",
        preset_dict=regex_subscription_dict_exclude,
    )


@pytest.fixture
def playlist_subscription_overrides(
    default_config: ConfigFile,
    regex_subscription_dict_match_and_exclude_override_variable: Dict[str, Any],
) -> Subscription:
    return Subscription.from_dict(
        config=default_config,
        preset_name="regex_using_overrides_test",
        preset_dict=regex_subscription_dict_match_and_exclude_override_variable,
    )


@pytest.fixture
def playlist_subscription_match_and_exclude(
    default_config: ConfigFile, regex_subscription_dict_match_and_exclude: Dict[str, Any]
) -> Subscription:
    return Subscription.from_dict(
        config=default_config,
        preset_name="regex_match_and_exclude_playlist_test",
        preset_dict=regex_subscription_dict_match_and_exclude,
    )


class TestRegex:
    def test_regex_success(self, playlist_subscription, output_directory):
        # Only dry run is needed to see if capture variables are created
        transaction_log = playlist_subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_regex.txt",
        )

    def test_regex_excludes_success(self, playlist_subscription_exclude, output_directory):
        # Should only contain the march video
        transaction_log = playlist_subscription_exclude.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_regex_exclude.txt",
        )

    def test_regex_match_and_excludes_success(
        self, playlist_subscription_match_and_exclude, output_directory
    ):
        # Should only contain the Feb 1st video
        transaction_log = playlist_subscription_match_and_exclude.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_regex_match_and_exclude.txt",
        )

    def test_regex_using_overrides_success(self, playlist_subscription_overrides, output_directory):
        # Should only contain the march video
        transaction_log = playlist_subscription_overrides.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_regex_overrides.txt",
        )

    def test_regex_fails_no_match(self, playlist_subscription_no_match_fails, output_directory):
        with pytest.raises(
            UserThrownRuntimeError,
            match=re.escape(
                "When running %regex_capture_many_required, no regex strings were captured"
            ),
        ):
            _ = playlist_subscription_no_match_fails.download(dry_run=True)

    def test_regex_fails_capture_group_is_entry_variable(
        self, regex_subscription_dict, default_config
    ):
        regex_subscription_dict["regex"]["from"]["playlist_uid"] = {
            "match": [".*http:\\/\\/(.+).com.*"],
            "capture_group_names": ["uid"],
        }

        with pytest.raises(
            ValidationException,
            match=re.escape(
                "Cannot use the variable name uid because it exists as a built-in "
                "ytdl-sub variable name."
            ),
        ):
            _ = Subscription.from_dict(
                config=default_config,
                preset_name="test_regex_fails_capture_group_is_entry_variable",
                preset_dict=regex_subscription_dict,
            )

    def test_regex_fails_capture_group_is_override_variable(
        self, regex_subscription_dict, default_config
    ):
        regex_subscription_dict["regex"]["from"]["playlist_uid"] = {
            "match": [".*http:\\/\\/(.+).com.*"],
            "capture_group_names": ["contains_regex_default"],
        }

        with pytest.raises(
            ValidationException,
            match=re.escape(
                "Override variable with name contains_regex_default cannot be used since it is "
                "added by a plugin."
            ),
        ):
            _ = Subscription.from_dict(
                config=default_config,
                preset_name="test_regex_fails_capture_group_is_override_variable",
                preset_dict=regex_subscription_dict,
            )

    def test_regex_fails_source_variable_does_not_exist(
        self, regex_subscription_dict, default_config
    ):
        regex_subscription_dict["regex"]["from"]["dne"] = copy.deepcopy(
            regex_subscription_dict["regex"]["from"]["title"]
        )
        with pytest.raises(
            ValidationException,
            match=re.escape("cannot regex capture 'dne' because it is not a defined variable"),
        ):
            _ = Subscription.from_dict(
                config=default_config,
                preset_name="test_regex_fails_source_variable_does_not_exist",
                preset_dict=regex_subscription_dict,
            )

    def test_regex_fails_unequal_defaults(self, regex_subscription_dict, default_config):
        regex_subscription_dict["regex"]["from"]["title"]["capture_group_defaults"] = ["1 != 2"]
        with pytest.raises(
            ValidationException,
            match=re.escape("number of defaults must match number of capture groups, 1 != 2"),
        ):
            _ = Subscription.from_dict(
                config=default_config,
                preset_name="test_regex_fails_unequal_defaults",
                preset_dict=regex_subscription_dict,
            )

    def test_regex_fails_unequal_capture_group_names(self, regex_subscription_dict, default_config):
        regex_subscription_dict["regex"]["from"]["title"]["capture_group_names"].append("unequal")
        with pytest.raises(
            ValidationException,
            match=re.escape(
                "number of capture group names must match number of capture groups, 3 != 2"
            ),
        ):
            _ = Subscription.from_dict(
                config=default_config,
                preset_name="test_regex_fails_unequal_capture_group_names",
                preset_dict=regex_subscription_dict,
            )
