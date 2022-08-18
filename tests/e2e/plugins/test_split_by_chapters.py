import pytest
from e2e.expected_download import assert_expected_downloads
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def yt_album_as_chapters_preset_dict(output_directory):
    return {
        "preset": "yt_album_as_chapters",
        "youtube": {"video_url": "youtube.com/watch?v=wtg7AetxuWo"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
            "postprocessor_args": {"ffmpeg": ["-bitexact"]},  # Must add this for reproducibility
        },
    }


class TestSplitByChapters:
    # TODO: fix dry run
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_video_with_chapters(
        self,
        youtube_audio_config,
        yt_album_as_chapters_preset_dict,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=youtube_audio_config,
            preset_name="split_by_chapters_video",
            preset_dict=yt_album_as_chapters_preset_dict,
        )

        transaction_log = subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"plugins/split_by_chapters_video{'-dry-run' if dry_run else ''}.txt",
            regenerate_transaction_log=True,
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/split_by_chapters_video.json",
            regenerate_expected_download_summary=True,
        )
