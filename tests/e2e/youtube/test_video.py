import pytest
from conftest import preset_dict_to_dl_args
from e2e.conftest import mock_run_from_cli
from e2e.expected_download import assert_expected_downloads
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def single_video_preset_dict(output_directory):
    return {
        "preset": "yt_music_video",
        "youtube": {"video_url": "https://youtube.com/watch?v=HKTNxEqsN3Q"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
        },
        "overrides": {"artist": "JMC"},
    }


@pytest.fixture
def single_video_preset_dict_dl_args(single_video_preset_dict):
    return preset_dict_to_dl_args(single_video_preset_dict)


class TestYoutubeVideo:
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_single_video_download(
        self,
        music_video_config,
        single_video_preset_dict,
        output_directory,
        dry_run,
    ):
        single_video_subscription = Subscription.from_dict(
            config=music_video_config,
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

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_single_video_download_from_cli_dl(
        self,
        music_video_config_path,
        single_video_preset_dict_dl_args,
        output_directory,
        dry_run,
    ):
        args = "--dry-run " if dry_run else ""
        args += f"--config {music_video_config_path} "
        args += f"dl {single_video_preset_dict_dl_args}"
        subscription_transaction_log = mock_run_from_cli(args=args)

        assert len(subscription_transaction_log) == 1
        transaction_log = subscription_transaction_log[0][1]

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

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_single_video_with_timestamp_chapters_download(
        self,
        timestamps_file_path,
        music_video_config,
        single_video_preset_dict,
        output_directory,
        dry_run,
    ):
        single_video_preset_dict["youtube"]["chapter_timestamps"] = timestamps_file_path
        single_video_subscription = Subscription.from_dict(
            config=music_video_config,
            preset_name="music_video_single_video_test",
            preset_dict=single_video_preset_dict,
        )

        transaction_log = single_video_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_video_with_chapter_timestamps.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="youtube/test_video_with_chapter_timestamps.json",
        )
