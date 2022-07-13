import pytest
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def regex_capture_subscription_dict(output_directory):
    return {
        "preset": "yt_music_video_playlist",
        "youtube": {"playlist_url": "https://youtube.com/playlist?list=PL5BC0FC26BECA5A35"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "best[height<=480]",
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
        "regex": {
            "skip_if_match_fails": False,
            "from": {
                "title": {
                    "match": [
                        "should not cap (.+) - (.+)",
                        ".*\\[(.+) - (.+)]",
                    ],
                },
                "description": {"match": [".*http:\\/\\/(.+).com.*"]},
                "upload_date_standardized": {
                    "match": ["([0-9]+)-([0-9]+)-27"],
                    "defaults": [
                        "First",
                        "Second",
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
            }
        },
    }


@pytest.fixture
def playlist_subscription(music_video_config, regex_capture_subscription_dict):
    playlist_preset = Preset.from_dict(
        config=music_video_config,
        preset_name="regex_capture_playlist_test",
        preset_dict=regex_capture_subscription_dict,
    )

    return Subscription.from_preset(
        preset=playlist_preset,
        config=music_video_config,
    )


class TestRegexCapture:
    def test_regex_capture_success(self, playlist_subscription, output_directory):
        # Only dry run is needed to see if capture variables are created
        transaction_log = playlist_subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_regex_mapping.txt",
        )
