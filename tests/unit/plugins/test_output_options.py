from typing import Dict

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.entries.entry import ytdl_sub_chapters_from_comments
from ytdl_sub.subscriptions.subscription import Subscription


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
        output_options_subscription_dict['output_options']['thumbnail_name'] = ""
        output_options_subscription_dict['output_options']['info_json_name'] = ""

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
