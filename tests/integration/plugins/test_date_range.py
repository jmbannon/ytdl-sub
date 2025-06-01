import re

import pytest

from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException


@pytest.fixture
def single_song_video_dict(output_directory):
    return {
        "download": "https://your.name.here",
        "output_options": {"output_directory": output_directory, "file_name": "will_error.mp4"},
        # test multi-tags compile
        "music_tags": {"genres": ["multi_tag_1", "multi_tag_2"]},
    }


class TestDateRange:
    def test_date_range(
        self,
        config,
        single_song_video_dict,
        output_directory,
        subscription_name,
        mock_download_collection_entries,
    ):
        ytdl_options = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=single_song_video_dict,
        ).get_ytdl_options(plugins=None, dry_run=False)

        assert ytdl_options.download_builder().to_dict() is False
