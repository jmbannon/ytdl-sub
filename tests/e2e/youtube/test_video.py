from unittest.mock import patch

import pytest
from conftest import preset_dict_to_dl_args
from e2e.conftest import mock_run_from_cli
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.entries.entry import Entry
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.system import IS_WINDOWS
from ytdl_sub.utils.thumbnail import try_convert_download_thumbnail


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


@pytest.fixture
def single_video_preset_dict_dl_args(single_video_preset_dict):
    return preset_dict_to_dl_args(single_video_preset_dict)


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

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_single_video_download_from_cli_dl(
        self,
        default_config_path,
        single_video_preset_dict_dl_args,
        output_directory,
        dry_run,
    ):
        # TODO: Fix CLI parsing on windows when dealing with spaces
        if IS_WINDOWS:
            return

        args = "--dry-run " if dry_run else ""
        args += f"--config {default_config_path} "
        args += f"dl {single_video_preset_dict_dl_args}"
        subscriptions = mock_run_from_cli(args=args)

        assert len(subscriptions) == 1
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=subscriptions[0].transaction_log,
            transaction_log_summary_file_name="youtube/test_video_cli.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="youtube/test_video_cli.json",
        )
