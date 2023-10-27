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
from ytdl_sub.utils.thumbnail import try_convert_download_thumbnail


@pytest.fixture
def single_video_preset_dict_old_video_tags_format(output_directory):
    return {
        "preset": "Jellyfin Music Videos",
        "download": "https://youtube.com/watch?v=HKTNxEqsN3Q",
        # override the output directory with our fixture-generated dir
        "output_options": {
            "output_directory": output_directory,
            "maintain_download_archive": False,
        },
        "embed_thumbnail": True,  # embed thumb into the video
        "format": "worst[ext=mp4]",  # download the worst format so it is fast
        # also test video tags
        "video_tags": {
            "tags": {
                "title": "{title}",
            }
        },
        "overrides": {"artist": "JMC"},
    }


@pytest.fixture
def single_video_preset_dict(output_directory):
    return {
        "preset": "Jellyfin Music Videos",
        "download": "https://youtube.com/watch?v=HKTNxEqsN3Q",
        # override the output directory with our fixture-generated dir
        "output_options": {
            "output_directory": output_directory,
            "maintain_download_archive": False,
        },
        "embed_thumbnail": True,  # embed thumb into the video
        "format": "worst[ext=mp4]",  # download the worst format so it is fast
        # also test video tags
        "video_tags": {
            "title": "{title}",
        },
        "overrides": {"artist": "JMC"},
    }


@pytest.fixture
def single_tv_show_video_nulled_values_preset_dict(output_directory):
    return {
        "preset": [
            "jellyfin_tv_show_by_date",
            "season_by_year__episode_by_download_index",
            "chunk_initial_download",
        ],
        # set file output fields to None
        "output_options": {
            "thumbnail_name": "",
            "info_json_name": "",
        },
        "format": "worst[ext=mp4]",
        "ytdl_options": {
            "max_downloads": 2,
        },
        # test override variables added by ytdl-sub
        "nfo_tags": {
            "tags": {
                "subscription_name": "{subscription_name}",
                "subscription_name_sanitized": "{subscription_name_sanitized}",
            }
        },
        "overrides": {
            "url": "https://www.youtube.com/@ProjectZombie603",
            "tv_show_name": "Project Zombie",
            "tv_show_directory": output_directory,
        },
    }


@pytest.fixture
def single_video_preset_dict_dl_args(single_video_preset_dict):
    return preset_dict_to_dl_args(single_video_preset_dict)


class TestYoutubeVideo:
    def test_single_video_old_video_tags_format_download(
        self,
        default_config,
        single_video_preset_dict_old_video_tags_format,
        output_directory,
    ):
        single_video_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="music_video_single_video_test",
            preset_dict=single_video_preset_dict_old_video_tags_format,
        )

        transaction_log = single_video_subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_video.txt",
        )

    @pytest.mark.parametrize("dry_run", [True])
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

    def test_single_video_download_missing_thumbnail(
        self,
        default_config,
        single_video_preset_dict,
        working_directory,
        output_directory,
    ):
        single_video_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="music_video_single_video_test",
            preset_dict=single_video_preset_dict,
        )

        def delete_entry_thumb(entry: Entry) -> None:
            FileHandler.delete(entry.get_download_thumbnail_path())
            try_convert_download_thumbnail(entry=entry)

        # Pretend the thumbnail did not download via returning nothing for its downloaded path
        with patch.object(YTDLP, "_EXTRACT_ENTRY_NUM_RETRIES", 1), patch.object(
            Entry, "try_get_ytdlp_download_thumbnail_path"
        ) as mock_ytdlp_path, patch(
            "ytdl_sub.downloaders.url.downloader.try_convert_download_thumbnail",
            side_effect=delete_entry_thumb,
        ):
            mock_ytdlp_path.return_value = None
            transaction_log = single_video_subscription.download(dry_run=False)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_video_missing_thumb.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name="youtube/test_video_missing_thumb.json",
        )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_single_video_download_from_cli_dl(
        self,
        default_config_path,
        single_video_preset_dict_dl_args,
        output_directory,
        dry_run,
    ):
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

    def test_single_video_nulled_values(
        self,
        channel_as_tv_show_config,
        single_tv_show_video_nulled_values_preset_dict,
        output_directory,
    ):
        single_video_subscription = Subscription.from_dict(
            config=channel_as_tv_show_config,
            preset_name="tv_video_nulled_values",
            preset_dict=single_tv_show_video_nulled_values_preset_dict,
        )

        transaction_log = single_video_subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_video_nulled_values.txt",
        )
