from typing import Dict

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.entries.entry import ytdl_sub_chapters_from_comments
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def file_convert_subscription_dict(output_directory) -> Dict:
    return {
        "preset": "Jellyfin Music Videos",
        "output_options": {"output_directory": output_directory},
        "overrides": {
            "music_video_artist": "JMC",
            "url": "https://your.name.here",
        },
        "file_convert": {
            "convert_to": "mkv",
            "convert_with": "ffmpeg",
            "ffmpeg_post_process_args": "-bitexact -vcodec copy -acodec copy -scodec mov_text",
        },
    }


class TestFileConvert:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_file_convert_custom_args(
        self,
        config,
        subscription_name,
        file_convert_subscription_dict,
        output_directory,
        mock_download_collection_entries,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=file_convert_subscription_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=False,
            num_urls=1,
            is_extracted_audio=False,
            is_dry_run=dry_run,
        ):
            transaction_log = subscription.download(dry_run=dry_run)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"plugins/file_convert/custom_ffmpeg_args.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/file_convert/custom_ffmpeg_args.json",
        )
