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


class TestMusicTags:
    def test_music_tags_errors_on_video(
        self,
        config,
        single_song_video_dict,
        output_directory,
        subscription_name,
        mock_download_collection_entries,
    ):
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=single_song_video_dict,
        )

        with (
            mock_download_collection_entries(
                is_youtube_channel=False, num_urls=1, is_extracted_audio=False, is_dry_run=True
            ),
            pytest.raises(
                ValidationException,
                match=re.escape(
                    f"Validation error in {subscription_name}.music_tags: music_tags plugin received a "
                    "video with the extension 'mp4'. Only audio files are supported for setting music "
                    "tags. Ensure you are converting the video to audio using the audio_extract "
                    "plugin."
                ),
            ),
        ):
            subscription.download(dry_run=True)
