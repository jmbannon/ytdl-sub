import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def subscription_dict(output_directory):
    return {
        "preset": "soundcloud_discography",
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp3]",
        },
        "overrides": {
            "track_artist": "j_b",
            "sc_artist_url": "https://soundcloud.com/jessebannon",
            "music_directory": output_directory,
        },
    }


class TestSoundcloudDiscography:
    """
    Downloads my (bad) SC recordings I made. Ensure the above files exist and have the
    expected md5 file hashes.
    """

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_discography_download(
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
            transaction_log_summary_file_name="soundcloud/test_soundcloud_discography.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="soundcloud/test_soundcloud_discography.json",
        )
