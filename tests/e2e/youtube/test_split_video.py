import pytest
from e2e.expected_download import assert_expected_downloads
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def subscription_dict(output_directory, timestamps_file_path):
    return {
        "preset": "yt_music_video",
        "youtube": {
            "download_strategy": "split_video",
            "video_url": "https://youtube.com/watch?v=HKTNxEqsN3Q",
            "split_timestamps": timestamps_file_path,
        },
        # override the output directory with our fixture-generated dir
        "output_options": {
            "output_directory": output_directory,
            "file_name": "{channel_sanitized} - {playlist_index}-{playlist_size}"
            ".{title_sanitized}.{ext}",
        },
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
        },
    }


####################################################################################################
# SINGLE VIDEO FIXTURES


@pytest.fixture
def single_video_subscription(music_video_config, subscription_dict):
    single_video_preset = Preset.from_dict(
        config=music_video_config,
        preset_name="split_video_test",
        preset_dict=subscription_dict,
    )

    return Subscription.from_preset(
        preset=single_video_preset,
        config=music_video_config,
    )


class TestPlaylistAsKodiMusicVideo:
    """
    Downloads my old minecraft youtube channel, pretends they are music videos. Ensure the above
    files exist and have the expected md5 file hashes.
    """

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_split_video_download(self, single_video_subscription, output_directory, dry_run):
        transaction_log = single_video_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_split_video.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="youtube/test_split_video.json",
        )
