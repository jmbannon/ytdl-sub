import re

import pytest
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import RegexNoMatchException


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
            "skip_if_match_fails": True,
            "from": {
                "title": {
                    "match": [
                        "should not cap (.+) - (.+)",
                        ".*\\[(.+) - (Feb.+)]",  # should filter out march video
                    ],
                },
                "description": {"match": [".*http:\\/\\/(.+).com.*"]},
                "upload_date_standardized": {
                    "match": ["([0-9]+)-([0-9]+)-27"],
                    "defaults": [
                        "First",
                        "Second containing {in_regex_default}",
                    ],
                },
                "artist": {"match": ["Never (.*) capture"], "defaults": ["Always default"]},
            },
        },
        "nfo_tags": {
            "tags": {
                "title_cap_1": "{title_capture_1}",
                "title_cap_2": "{title_capture_2}",
                "desc_cap": "{description_capture_1}",
                "upload_date_both_caps": "{upload_date_standardized_capture_1} and {upload_date_standardized_capture_2}",
                "artist_cap_always_default": "{artist_capture_1}",
                "override_with_capture_variable": "{contains_regex_default}"
            }
        },
        "overrides": {
            "in_regex_default": "in regex default",
            "contains_regex_default": "contains {title_capture_1}"
        }
    }


@pytest.fixture
def regex_subscription_dict_no_match_fails(regex_subscription_dict):
    # tests that skip_if_match_fails defaults to False
    del regex_subscription_dict["regex"]["skip_if_match_fails"]
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
