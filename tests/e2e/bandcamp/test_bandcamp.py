import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def subscription_dict(output_directory):
    return {
        "preset": "albums_from_playlists",
        "ytdl_options": {
            "max_downloads": 20,
        },
        "regex": {
            "skip_if_match_fails": False,  # Error if regex match fails
            "from": {
                "title": {
                    "match": ["^(.*) - (.*)"],  # Captures 'title' from 'Emily Hopkins - title'
                    "capture_group_names": [
                        "captured_track_artist",
                        "captured_track_title",
                    ],
                }
            },
        },
        "overrides": {
            "url": "https://funkypselicave.bandcamp.com/",
            "track_title": "{captured_track_title}",
            "track_artist": "{captured_track_artist}",
            "music_directory": output_directory,
        },
    }


class TestBandcamp:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_download_artist_url(
        self,
        subscription_dict,
        music_audio_config,
        output_directory,
        dry_run,
    ):
        discography_subscription = Subscription.from_dict(
            preset_dict=subscription_dict,
            preset_name="jb",
            config=music_audio_config,
        )
        transaction_log = discography_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="bandcamp/test_artist_url.txt",
            regenerate_transaction_log=True,
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="bandcamp/test_artist_url.json",
            regenerate_expected_download_summary=True,
        )
