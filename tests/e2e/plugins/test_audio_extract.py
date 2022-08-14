import mergedeep
import pytest
from e2e.expected_download import assert_expected_downloads
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def single_song_preset_dict(output_directory):
    return {
        "preset": "yt_song",
        "youtube": {"video_url": "https://www.youtube.com/watch?v=2lAe1cqCOXo"},
        "output_options": {"output_directory": output_directory},
    }


class TestAudioExtract:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_audio_extract_single_song(
        self,
        youtube_audio_config,
        single_song_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=youtube_audio_config,
            preset_name="single_song_test",
            preset_dict=single_song_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/test_audio_extract_single.txt",
            regenerate_transaction_log=True,
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/test_audio_extract_single.json",
            regenerate_expected_download_summary=True,
        )
