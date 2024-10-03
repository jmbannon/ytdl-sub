from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches
from mergedeep import mergedeep

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.entries.entry import Entry
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.thumbnail import try_convert_download_thumbnail


@pytest.fixture
def output_options_subscription_dict(output_directory) -> Dict:
    return {
        "preset": [
            "jellyfin_tv_show_by_date",
            "season_by_year__episode_by_download_index",
            "chunk_initial_download",
        ],
        "output_options": {
            "output_directory": output_directory,
        },
        "overrides": {
            "tv_show_name": "JMC",
            "url": "https://your.name.here",
        },
    }


class TestOutputOptions:

    @classmethod
    def _ensure_subscription_migrates(
        cls,
        config: ConfigFile,
        subscription_name: str,
        subscription_dict: Dict,
        output_directory: Path,
    ):
        # Ensure download archive migrates
        mergedeep.merge(
            subscription_dict,
            {
                "output_options": {
                    "migrated_download_archive_name": ".ytdl-sub-{tv_show_name_sanitized}-download-archive.json"
                }
            },
        )
        migrated_subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=subscription_dict,
        )
        transaction_log = migrated_subscription.download()

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist_archive_migrated.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name="youtube/test_playlist_archive_migrated.json",
        )

        # Ensure no changes after migration
        transaction_log = migrated_subscription.download()
        assert transaction_log.is_empty
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name="youtube/test_playlist_archive_migrated.json",
        )

    def test_download_archive_migration(
        self,
        config: ConfigFile,
        subscription_name: str,
        output_options_subscription_dict: Dict,
        output_directory: str,
        mock_download_collection_entries,
    ):
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=output_options_subscription_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=False,
            num_urls=1,
            is_extracted_audio=False,
            is_dry_run=False,
        ):
            transaction_log = subscription.download(dry_run=False)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/output_options/pre_migration.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name="plugins/output_options/pre_migration.json",
        )

        output_options_subscription_dict["output_options"][
            "migrated_download_archive_name"
        ] = ".ytdl-sub-{tv_show_name_sanitized}-migrated-download-archive.json"
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=output_options_subscription_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=False,
            num_urls=0,
        ):
            transaction_log = subscription.download(dry_run=False)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/output_options/post_migration.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name="plugins/output_options/post_migration.json",
        )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_empty_info_json_and_thumb(
        self,
        config: ConfigFile,
        subscription_name: str,
        output_options_subscription_dict: Dict,
        output_directory: str,
        mock_download_collection_entries,
        dry_run,
    ):
        output_options_subscription_dict["output_options"]["thumbnail_name"] = ""
        output_options_subscription_dict["output_options"]["info_json_name"] = ""

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=output_options_subscription_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=False,
            num_urls=1,
            is_extracted_audio=False,
            is_dry_run=dry_run,
        ):
            transaction_log = subscription.download(dry_run=dry_run)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/output_options/empty_info_json_thumb.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/output_options/empty_info_json_thumb.json",
        )

    def test_missing_thumbnail(
        self,
        config: ConfigFile,
        subscription_name: str,
        output_options_subscription_dict: Dict,
        working_directory,
        output_directory,
        mock_download_collection_entries,
    ):
        single_video_subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=output_options_subscription_dict,
        )

        def delete_entry_thumb(entry: Entry) -> None:
            FileHandler.delete(entry.get_download_thumbnail_path())
            try_convert_download_thumbnail(entry=entry)

        # Pretend the thumbnail did not download via returning nothing for its downloaded path
        with (
            mock_download_collection_entries(
                is_youtube_channel=False,
                num_urls=1,
                is_extracted_audio=False,
                is_dry_run=False,
            ),
            patch.object(YTDLP, "_EXTRACT_ENTRY_NUM_RETRIES", 1),
            patch.object(Entry, "try_get_ytdlp_download_thumbnail_path") as mock_ytdlp_path,
            patch(
                "ytdl_sub.downloaders.url.downloader.try_convert_download_thumbnail",
                side_effect=delete_entry_thumb,
            ),
        ):
            mock_ytdlp_path.return_value = None
            transaction_log = single_video_subscription.download(dry_run=False)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/output_options/test_missing_thumb.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name="plugins/output_options/test_missing_thumb.json",
        )
