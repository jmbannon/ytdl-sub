from pathlib import Path
from typing import Dict

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.prebuilt_presets.music_videos import MusicVideoPresets
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.mark.parametrize("music_video_preset", MusicVideoPresets.preset_names)
class TestPrebuiltMusicVideoPresets:
    def test_presets_run(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        music_video_preset: str,
    ):
        expected_summary_name = f"unit/music_videos/{music_video_preset}"

        preset_dict = {
            "preset": [
                music_video_preset,
            ],
            "overrides": {
                "url": "https://your.name.here",
                "music_video_directory": output_directory,
            },
        }

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=preset_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=False, num_urls=1, is_extracted_audio=False
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


@pytest.mark.parametrize("music_video_preset", MusicVideoPresets.preset_names)
@pytest.mark.parametrize("multi_url", [True, False])
class TestPrebuiltMusicVideoPresetsWithCategories:

    def _preset_dict(
        self,
        output_directory: Path,
        music_video_preset: str,
        multi_url: bool,
    ) -> Dict:
        subscription_dict = {"Music Videos": ["https://your.name.here"]}

        if multi_url:
            subscription_dict["Concerts"] = [
                {"url": "https://your.name.here2", "title": "Custom Title"}
            ]

        preset_dict = {
            "preset": [
                music_video_preset,
            ],
            "overrides": {
                "music_video_directory": output_directory,
                "subscription_map": subscription_dict,
            },
        }

        return preset_dict

    def test_presets_run(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        music_video_preset: str,
        multi_url: bool,
    ):
        expected_summary_name = (
            f"unit/music_videos/{music_video_preset} Categorized/multi_url_{multi_url}"
        )

        preset_dict = self._preset_dict(
            output_directory=output_directory,
            music_video_preset=music_video_preset,
            multi_url=multi_url,
        )

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=preset_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=False, num_urls=2 if multi_url else 1, is_extracted_audio=False
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
