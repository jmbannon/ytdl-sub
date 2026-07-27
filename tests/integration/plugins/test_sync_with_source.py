import contextlib
import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional
from unittest.mock import patch

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.downloaders.url.downloader import MultiUrlDownloader
from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.plugins.throttle_protection import ThrottleProtectionPlugin
from ytdl_sub.subscriptions.subscription import Subscription

ARCHIVE_FILE_NAME = ".ytdl-sub-subscription_test-download-archive.json"


@pytest.fixture
def sync_subscription_dict(output_directory: str) -> Dict:
    return {
        "download": {"url": "https://your.name.here"},
        "output_options": {
            "output_directory": output_directory,
            "file_name": "{title_sanitized}.{ext}",
            "maintain_download_archive": True,
            "sync_with_source": True,
        },
    }


@contextlib.contextmanager
def _mock_source(
    mock_entry_dict_factory: Callable,
    uids: List[str],
    truncation_reason: Optional[str] = None,
):
    """
    Patches out the metadata fetch so the "source" is whatever uids are passed in.
    Simulates a video being removed from a playlist by passing fewer uids on a later run.

    Entry dicts are built lazily within the patch because creating them writes the mock
    media files into the working directory, which must be empty when a download begins.
    """

    def _extract_info_via_info_json(*args, **kwargs) -> List[Dict]:
        _ = args
        if truncation_reason is not None:
            kwargs["truncation_reasons"].append(truncation_reason)

        return [
            mock_entry_dict_factory(
                uid=uid,
                upload_date=f"2021080{idx + 1}",
                playlist_index=idx + 1,
                playlist_count=len(uids),
            )
            for idx, uid in enumerate(uids)
        ]

    with (
        patch.object(YTDLP, "extract_info_via_info_json", new=_extract_info_via_info_json),
        patch.object(
            MultiUrlDownloader, "_extract_entry_info_with_retry", new=lambda _, entry: entry
        ),
        patch.object(ThrottleProtectionPlugin, "perform_sleep", new=lambda _1, _2: None),
    ):
        yield


def _archived_uids(output_directory: str) -> List[str]:
    with open(Path(output_directory) / ARCHIVE_FILE_NAME, "r", encoding="utf-8") as archive_file:
        return sorted(json.load(archive_file).keys())


def _output_files(output_directory: str) -> List[str]:
    return sorted(
        file_name
        for file_name in os.listdir(output_directory)
        if not file_name.startswith(".ytdl-sub")
    )


class TestSyncWithSource:
    @classmethod
    def _subscription(cls, config: ConfigFile, subscription_name: str, subscription_dict: Dict):
        return Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=subscription_dict,
        )

    def test_entry_removed_from_source_is_deleted(
        self,
        config: ConfigFile,
        subscription_name: str,
        sync_subscription_dict: Dict,
        output_directory: str,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = self._subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        assert _archived_uids(output_directory) == ["v1", "v2", "v3"]
        assert _output_files(output_directory) == [
            "Mock Entry v1.mp4",
            "Mock Entry v2.mp4",
            "Mock Entry v3.mp4",
        ]

        # v2 is removed from the source
        with _mock_source(mock_entry_dict_factory, ["v1", "v3"]):
            subscription.download(dry_run=False)

        assert _archived_uids(output_directory) == ["v1", "v3"]
        assert _output_files(output_directory) == ["Mock Entry v1.mp4", "Mock Entry v3.mp4"]

    def test_disabled_by_default_keeps_removed_entry(
        self,
        config: ConfigFile,
        subscription_name: str,
        sync_subscription_dict: Dict,
        output_directory: str,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        del sync_subscription_dict["output_options"]["sync_with_source"]
        subscription = self._subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        with _mock_source(mock_entry_dict_factory, ["v1", "v3"]):
            subscription.download(dry_run=False)

        assert _archived_uids(output_directory) == ["v1", "v2", "v3"]
        assert len(_output_files(output_directory)) == 3

    def test_empty_source_does_not_delete_everything(
        self,
        config: ConfigFile,
        subscription_name: str,
        sync_subscription_dict: Dict,
        output_directory: str,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = self._subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        with _mock_source(mock_entry_dict_factory, []):
            subscription.download(dry_run=False)

        assert _archived_uids(output_directory) == ["v1", "v2", "v3"]
        assert len(_output_files(output_directory)) == 3

    def test_truncated_metadata_does_not_delete_anything(
        self,
        config: ConfigFile,
        subscription_name: str,
        sync_subscription_dict: Dict,
        output_directory: str,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = self._subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        # The source only enumerated v1 before stopping early, which must not be read
        # as v2 and v3 having been removed
        with _mock_source(
            mock_entry_dict_factory, ["v1"], truncation_reason="ExistingVideoReached"
        ):
            subscription.download(dry_run=False)

        assert _archived_uids(output_directory) == ["v1", "v2", "v3"]
        assert len(_output_files(output_directory)) == 3

    def test_dry_run_does_not_delete(
        self,
        config: ConfigFile,
        subscription_name: str,
        sync_subscription_dict: Dict,
        output_directory: str,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = self._subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        with _mock_source(mock_entry_dict_factory, ["v1", "v3"]):
            transaction_log = subscription.download(dry_run=True)

        assert "Mock Entry v2.mp4" in transaction_log.to_output_message(output_directory)
        assert _archived_uids(output_directory) == ["v1", "v2", "v3"]
        assert len(_output_files(output_directory)) == 3
