from typing import Dict

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def square_thumbnail_subscription_dict(output_directory) -> Dict:
    return {
        "preset": "Jellyfin Music Videos",
        "output_options": {"output_directory": output_directory},
        "square_thumbnail": "{perform_square_thumbnail}",
        "embed_thumbnail": "{perform_embed_thumbnail}",
        "overrides": {
            "music_video_artist": "JMC",
            "url": "https://your.name.here",
            "perform_square_thumbnail": True,
            "perform_embed_thumbnail": False
        },
    }


class TestThumbnailPlugins:
    @pytest.mark.parametrize("dry_run", [True, False])
    @pytest.mark.parametrize("embed_thumbnail", [True, False])
    def test_thumbnail(
        self,
        config,
        subscription_name,
        square_thumbnail_subscription_dict,
        output_directory,
        mock_download_collection_entries,
        dry_run,
        embed_thumbnail,
    ):
        square_thumbnail_subscription_dict["overrides"]["perform_embed_thumbnail"] = embed_thumbnail

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=square_thumbnail_subscription_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=False,
            num_urls=1,
            is_extracted_audio=False,
            is_dry_run=dry_run,
        ):
            transaction_log = subscription.download(dry_run=dry_run)

        expected_filename = "square_thumbnail"
        if embed_thumbnail:
            expected_filename = "embedded_square_thumbnail"

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"plugins/thumbnail/{expected_filename}.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name=f"plugins/thumbnail/{expected_filename}.json",
        )
