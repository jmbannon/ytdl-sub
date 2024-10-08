import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches
from resources import DISABLE_YOUTUBE_TESTS

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def single_video_preset_dict(output_directory):
    return {
        "preset": "Jellyfin Music Videos",
        "download": "https://youtube.com/watch?v=HKTNxEqsN3Q",
        # override the output directory with our fixture-generated dir
        "output_options": {
            "maintain_download_archive": False,
        },
        "embed_thumbnail": True,  # embed thumb into the video
        "format": "worst[ext=mp4]",  # download the worst format so it is fast
        # also test video tags
        "video_tags": {
            "title": "{title}",
        },
        "overrides": {
            "music_video_artist": "JMC",
            "music_video_directory": output_directory,
            "test_override_map": {"{music_video_artist}": "{music_video_directory}"},
            "test_override_map_get": "{ %map_get(test_override_map, music_video_artist) }",
        },
    }


@pytest.mark.skipif(DISABLE_YOUTUBE_TESTS, reason="YouTube tests cannot run in GH")
class TestYoutubeVideo:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_single_video_download(
        self,
        default_config,
        single_video_preset_dict,
        output_directory,
        dry_run,
    ):
        single_video_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="music_video_single_video_test",
            preset_dict=single_video_preset_dict,
        )

        transaction_log = single_video_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_video.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="youtube/test_video.json",
        )
