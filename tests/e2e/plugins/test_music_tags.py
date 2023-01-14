import re

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException


@pytest.fixture
def single_song_video_dict(output_directory):
    return {
        "download": {
            "download_strategy": "url",
            "url": "https://www.youtube.com/watch?v=2lAe1cqCOXo",
        },
        "output_options": {"output_directory": output_directory, "file_name": "will_error.mp4"},
        # test multi-tags
        "music_tags": {"embed_thumbnail": True, "tags": {"genres": ["multi_tag_1", "multi_tag_2"]}},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
    }


class TestMusicTags:
    def test_music_tags_errors_on_video(
        self,
        music_audio_config,
        single_song_video_dict,
        output_directory,
    ):
        subscription = Subscription.from_dict(
            config=music_audio_config,
            preset_name="single_song_test",
            preset_dict=single_song_video_dict,
        )

        with pytest.raises(
            ValidationException,
            match=re.escape(
                "Validation error in single_song_test.music_tags: music_tags plugin received a "
                "video with the extension 'mp4'. Only audio files are supported for setting music "
                "tags. Ensure you are converting the video to audio using the audio_extract "
                "plugin."
            ),
        ):
            subscription.download(dry_run=True)
