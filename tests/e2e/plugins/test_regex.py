import copy
import re

import pytest
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import RegexNoMatchException
from ytdl_sub.utils.exceptions import ValidationException


@pytest.fixture
def regex_subscription_dict(output_directory):
    return {
        "preset": "yt_music_video_playlist",
        "youtube": {"playlist_url": "https://youtube.com/playlist?list=PL5BC0FC26BECA5A35"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "best[height<=480]",
        },
        "regex": {
            # tests that skip_if_match_fails defaults to True
            "from": {
                "title": {
                    "match": [
                        "should not cap (.+) - (.+)",
                        ".*\\[(.+) - (Feb.+)]",  # should filter out march video
                    ],
                    "capture_group_names": ["title_type", "title_date"],
                },
                "description": {
                    "match": [".*http:\\/\\/(.+).com.*"],
                    "capture_group_names": ["description_website"],
                },
                "upload_date_standardized": {
                    "match": ["([0-9]+)-([0-9]+)-27"],
                    "capture_group_names": [
                        "upload_captured_year",
                        "upload_captured_month",
                    ],
                    "capture_group_defaults": [
                        "First",
                        "Second containing {in_regex_default}",
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
            "in_regex_default": "in regex default",
            "contains_regex_default": "contains {title_type}",
            "contains_regex_sanitized_default": "contains {title_type_sanitized}",
        },
    }


@pytest.fixture
def regex_subscription_dict_no_match_fails(regex_subscription_dict):
    regex_subscription_dict["regex"]["skip_if_match_fails"] = False
    return regex_subscription_dict


@pytest.fixture
def playlist_subscription(music_video_config, regex_subscription_dict):
    playlist_preset = Preset.from_dict(
        config=music_video_config,
        preset_name="regex_capture_playlist_test",
        preset_dict=regex_subscription_dict,
    )

    return Subscription.from_preset(
        preset=playlist_preset,
        config=music_video_config,
    )


@pytest.fixture
def playlist_subscription_no_match_fails(
    music_video_config, regex_subscription_dict_no_match_fails
):
    playlist_preset = Preset.from_dict(
        config=music_video_config,
        preset_name="regex_capture_playlist_test",
        preset_dict=regex_subscription_dict_no_match_fails,
    )

    return Subscription.from_preset(
        preset=playlist_preset,
        config=music_video_config,
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

    def test_regex_fails_no_match(self, playlist_subscription_no_match_fails, output_directory):
        with pytest.raises(
            RegexNoMatchException,
            match=re.escape(
                "Regex failed to match 'title' from 'Jesse's Minecraft Server [Trailer - Mar.21]'"
            ),
        ):
            _ = playlist_subscription_no_match_fails.download(dry_run=True)

    def test_regex_fails_capture_group_is_source_variable(
        self, regex_subscription_dict, music_video_config
    ):
        regex_subscription_dict["regex"]["from"]["title"]["capture_group_names"][0] = "uid"
        with pytest.raises(
            ValidationException,
            match=re.escape(
                "'uid' cannot be used as a capture group name because it is a source variable"
            ),
        ):
            _ = Subscription.from_dict(
                config=music_video_config,
                preset_name="test_regex_fails_capture_group_is_source_variable",
                preset_dict=regex_subscription_dict,
            )

    def test_regex_fails_capture_group_is_override_variable(
        self, regex_subscription_dict, music_video_config
    ):
        regex_subscription_dict["regex"]["from"]["title"]["capture_group_names"][
            0
        ] = "in_regex_default"
        with pytest.raises(
            ValidationException,
            match=re.escape(
                "'in_regex_default' cannot be used as a capture group name because it is an override variable"
            ),
        ):
            _ = Subscription.from_dict(
                config=music_video_config,
                preset_name="test_regex_fails_capture_group_is_override_variable",
                preset_dict=regex_subscription_dict,
            )

    def test_regex_fails_source_variable_does_not_exist(
        self, regex_subscription_dict, music_video_config
    ):
        regex_subscription_dict["regex"]["from"]["dne"] = copy.deepcopy(
            regex_subscription_dict["regex"]["from"]["title"]
        )
        with pytest.raises(
            ValidationException,
            match=re.escape("cannot regex capture 'dne' because it is not a source variable"),
        ):
            _ = Subscription.from_dict(
                config=music_video_config,
                preset_name="test_regex_fails_source_variable_does_not_exist",
                preset_dict=regex_subscription_dict,
            )

    def test_regex_fails_unequal_defaults(self, regex_subscription_dict, music_video_config):
        regex_subscription_dict["regex"]["from"]["title"]["capture_group_defaults"] = ["1 != 2"]
        with pytest.raises(
            ValidationException,
            match=re.escape("number of defaults must match number of capture groups, 1 != 2"),
        ):
            _ = Subscription.from_dict(
                config=music_video_config,
                preset_name="test_regex_fails_unequal_defaults",
                preset_dict=regex_subscription_dict,
            )

    def test_regex_fails_unequal_capture_group_names(
        self, regex_subscription_dict, music_video_config
    ):
        regex_subscription_dict["regex"]["from"]["title"]["capture_group_names"].append("unequal")
        with pytest.raises(
            ValidationException,
            match=re.escape(
                "number of capture group names must match number of capture groups, 3 != 2"
            ),
        ):
            _ = Subscription.from_dict(
                config=music_video_config,
                preset_name="test_regex_fails_unequal_capture_group_names",
                preset_dict=regex_subscription_dict,
            )
