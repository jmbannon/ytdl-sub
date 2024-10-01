import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.prebuilt_presets.music import MusicPresets
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.mark.parametrize("music_preset", MusicPresets.preset_names)
class TestPrebuiltMusicPresets:

    def test_presets_run(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        music_preset: str,
    ):
        expected_summary_name = f"unit/music/{music_preset}"

        preset_dict = {
            "preset": [
                music_preset,
            ],
            "overrides": {
                "url": "https://your.name.here",
                "music_directory": output_directory,
            },
        }

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=preset_dict,
        )

        num_urls = 1
        if music_preset == "SoundCloud Discography":
            num_urls = 2  # simulate /albums and /tracks

        with mock_download_collection_entries(
            is_youtube_channel=False, num_urls=num_urls, is_extracted_audio=True
        ):
            transaction_log = subscription.download(dry_run=False)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"{expected_summary_name}.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name=f"{expected_summary_name}.json",
        )
