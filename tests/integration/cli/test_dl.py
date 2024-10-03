from typing import Dict
from unittest.mock import patch

import pytest
from conftest import mock_run_from_cli
from conftest import preset_dict_to_dl_args
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.cli.parsers.dl import DownloadArgsParser
from ytdl_sub.utils.system import IS_WINDOWS


@pytest.fixture
def dl_subscription_dict(output_directory) -> Dict:
    return {
        "preset": "Jellyfin Music Videos",
        "overrides": {
            "music_video_artist": "JMC",
            "music_video_directory": output_directory,
            "url": "https://your.name.here",
        },
        "nfo_tags": {"tags": {"custom_tag": "{%array_at( ['hi', 'mom'], 1 )}"}},
    }


class TestCliDl:
    @pytest.mark.parametrize("config_provided", [True, False])
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_cli_dl_command(
        self,
        default_config_path: str,
        subscription_name: str,
        dl_subscription_dict: Dict,
        output_directory: str,
        mock_download_collection_entries,
        config_provided: bool,
        dry_run: bool,
    ):
        # Skip this combo to save time and to avoid mocking working dir
        if not config_provided and not dry_run:
            return

        # TODO: Fix CLI parsing on windows when dealing with spaces
        if IS_WINDOWS:
            return

        args = "--dry-run " if dry_run else ""
        args += f"--config {default_config_path} " if config_provided else ""
        args += f"dl {preset_dict_to_dl_args(dl_subscription_dict)} "

        with (
            patch.object(DownloadArgsParser, "get_dl_subscription_name") as mock_subscription_name,
            mock_download_collection_entries(
                is_youtube_channel=False,
                num_urls=1,
                is_extracted_audio=False,
                is_dry_run=dry_run,
            ),
        ):
            mock_subscription_name.return_value = subscription_name
            subscriptions = mock_run_from_cli(args=args)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=subscriptions[0].transaction_log,
            transaction_log_summary_file_name="dl/test_cli_dl_command.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="dl/test_cli_dl_command.json",
        )
