from typing import Dict

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches
from integration.plugins.conftest import mock_chapters_class
from mergedeep import mergedeep

from ytdl_sub.entries.entry import ytdl_sub_chapters_from_comments
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def chapters_base_subscription_dict(output_directory) -> Dict:
    return {
        "preset": "Jellyfin Music Videos",
        "output_options": {"output_directory": output_directory},
        "overrides": {
            "music_video_artist": "JMC",
            "url": "https://your.name.here",
            "enable_sponsorblock": "False",
        },
    }


@pytest.fixture
def sponsorblock_disabled_dict(chapters_base_subscription_dict) -> Dict:
    mergedeep.merge(
        chapters_base_subscription_dict,
        {
            "chapters": {
                "enable": "{enable_sponsorblock}",
                "sponsorblock_categories": [
                    "outro",
                    "selfpromo",
                    "preview",
                    "interaction",
                    "sponsor",
                    "music_offtopic",
                    "intro",
                ],
                "remove_sponsorblock_categories": "all",
                "remove_chapters_regex": [
                    "Intro",
                    "Outro",
                ],
            },
            "overrides": {
                "enable_sponsorblock": "False",
            },
        },
    )
    return chapters_base_subscription_dict


@pytest.fixture
def chapters_from_comments_subscription_dict(chapters_base_subscription_dict) -> Dict:
    mergedeep.merge(
        chapters_base_subscription_dict,
        {
            "chapters": {
                "embed_chapters": True,
                "allow_chapters_from_comments": True,
            },
        },
    )
    return chapters_base_subscription_dict


class TestChapters:
    def test_chapters_disabled_respected(
        self,
        config,
        subscription_name,
        sponsorblock_disabled_dict,
        output_directory,
        mock_download_collection_entries,
    ):
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=sponsorblock_disabled_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=False, num_urls=1, is_extracted_audio=False, is_dry_run=True
        ):
            _ = subscription.download(dry_run=True)

        script = subscription.overrides.script
        assert script.get(ytdl_sub_chapters_from_comments.variable_name).native == ""

    @pytest.mark.usefixtures(mock_chapters_class.__name__)
    @pytest.mark.parametrize("dry_run", [True, False])
    def test_chapters_from_comments(
        self,
        config,
        subscription_name,
        chapters_from_comments_subscription_dict,
        mock_download_collection_entries,
        output_directory,
        dry_run,
    ):
        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=chapters_from_comments_subscription_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=False, num_urls=1, is_dry_run=dry_run
        ):
            transaction_log = subscription.download(dry_run=dry_run)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="plugins/chapters/test_chapters_from_comments.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="plugins/chapters/test_chapters_from_comments.json",
        )
