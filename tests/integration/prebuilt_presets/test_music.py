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
                "subscription_value": "https://your.name.here",
                "music_directory": output_directory,
            },
        }

        num_urls = 1
        if music_preset in {"YouTube Releases", "YouTube Full Albums"}:
            del preset_dict["overrides"]["subscription_value"]
            preset_dict["overrides"]["subscription_array"] = [
                "https://your.name.here",
                "https://your.name.here.2",
            ]
            num_urls = 2
        elif music_preset == "SoundCloud Discography":
            num_urls = 2  # simulate albums + tracks

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=preset_dict,
        )

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
