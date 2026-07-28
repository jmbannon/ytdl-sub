import contextlib
import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional
from unittest.mock import patch

import pytest
from resources import copy_file_fixture
from yt_dlp.utils import ExistingVideoReached

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
    mock_downloaded_file_path: Callable,
    mock_entry_dict_factory: Callable,
    uids: List[str],
    truncate_after: Optional[int] = None,
):
    """
    Patches the inner ``extract_info`` rather than ``extract_info_via_info_json`` so that the
    real metadata collection runs. This includes yt-dlp's behavior of writing no info.json for
    an entry already recorded in the download archive, which is what distinguishes an entry
    removed from the source from an entry that is simply already downloaded.

    Simulates a video being removed from a playlist by passing fewer uids on a later run, and
    metadata collection stopping early by setting ``truncate_after``.
    """

    def _extract_info(ytdl_options_overrides: Dict, **kwargs) -> Dict:
        _ = kwargs
        archived_ids = set()
        archive_path = ytdl_options_overrides.get("download_archive")
        if archive_path and os.path.isfile(archive_path):
            with open(archive_path, "r", encoding="utf-8") as archive_file:
                archived_ids = {line.split()[-1] for line in archive_file if line.strip()}

        num_written = 0
        for idx, uid in enumerate(uids):
            # yt-dlp writes no info.json for an entry already in the download archive
            if uid in archived_ids:
                continue

            if truncate_after is not None and num_written >= truncate_after:
                raise ExistingVideoReached()

            entry_dict = mock_entry_dict_factory(
                uid=uid,
                upload_date=f"2021080{idx + 1}",
                playlist_index=idx + 1,
                playlist_count=len(uids),
                mock_download_to_working_dir=False,
            )
            with open(
                mock_downloaded_file_path(f"{uid}.info.json"), "w", encoding="utf-8"
            ) as info_json_file:
                json.dump(entry_dict, info_json_file)

            num_written += 1

        return {}

    def _mock_entry_download(_, entry):
        # The media file appears at download time, since metadata collection runs with
        # skip_download
        copy_file_fixture(
            fixture_name="sample_vid.mp4",
            output_file_path=mock_downloaded_file_path(f"{entry.uid}.mp4"),
        )
        return entry

    with (
        patch.object(YTDLP, "extract_info", new=_extract_info),
        patch.object(
            MultiUrlDownloader, "_extract_entry_info_with_retry", new=_mock_entry_download
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


def _subscription(config: ConfigFile, subscription_name: str, subscription_dict: Dict):
    return Subscription.from_dict(
        config=config,
        preset_name=subscription_name,
        preset_dict=subscription_dict,
    )


class TestSyncWithSource:
    def test_entry_removed_from_source_is_deleted(
        self,
        config: ConfigFile,
        subscription_name: str,
        sync_subscription_dict: Dict,
        output_directory: str,
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = _subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        assert _archived_uids(output_directory) == ["v1", "v2", "v3"]
        assert _output_files(output_directory) == [
            "Mock Entry v1.mp4",
            "Mock Entry v2.mp4",
            "Mock Entry v3.mp4",
        ]

        # v2 is removed from the source
        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v3"]):
            subscription.download(dry_run=False)

        assert _archived_uids(output_directory) == ["v1", "v3"]
        assert _output_files(output_directory) == ["Mock Entry v1.mp4", "Mock Entry v3.mp4"]

    def test_previously_downloaded_entries_survive_a_new_entry(
        self,
        config: ConfigFile,
        subscription_name: str,
        sync_subscription_dict: Dict,
        output_directory: str,
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = _subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        # A new entry appears. v1-v3 are in the download archive, so yt-dlp would omit them
        # from the metadata fetch entirely if the archive were not withheld
        with _mock_source(
            mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v2", "v3", "v4"]
        ):
            subscription.download(dry_run=False)

        assert _archived_uids(output_directory) == ["v1", "v2", "v3", "v4"]
        assert len(_output_files(output_directory)) == 4

    def test_disabled_by_default_keeps_removed_entry(
        self,
        config: ConfigFile,
        subscription_name: str,
        sync_subscription_dict: Dict,
        output_directory: str,
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        del sync_subscription_dict["output_options"]["sync_with_source"]
        subscription = _subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v3"]):
            subscription.download(dry_run=False)

        assert _archived_uids(output_directory) == ["v1", "v2", "v3"]
        assert len(_output_files(output_directory)) == 3

    def test_empty_source_does_not_delete_everything(
        self,
        config: ConfigFile,
        subscription_name: str,
        sync_subscription_dict: Dict,
        output_directory: str,
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = _subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, []):
            subscription.download(dry_run=False)

        assert _archived_uids(output_directory) == ["v1", "v2", "v3"]
        assert len(_output_files(output_directory)) == 3

    def test_truncated_metadata_does_not_delete_anything(
        self,
        config: ConfigFile,
        subscription_name: str,
        sync_subscription_dict: Dict,
        output_directory: str,
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = _subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        # Metadata collection stops after v1, which must not be read as v2 and v3 having
        # been removed from the source
        with _mock_source(
            mock_downloaded_file_path,
            mock_entry_dict_factory,
            ["v1", "v2", "v3"],
            truncate_after=1,
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
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = _subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v3"]):
            transaction_log = subscription.download(dry_run=True)

        assert "Mock Entry v2.mp4" in transaction_log.to_output_message(output_directory)
        assert _archived_uids(output_directory) == ["v1", "v2", "v3"]
        assert len(_output_files(output_directory)) == 3

    def test_already_downloaded_entries_are_not_redownloaded(
        self,
        config: ConfigFile,
        subscription_name: str,
        sync_subscription_dict: Dict,
        output_directory: str,
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = _subscription(config, subscription_name, sync_subscription_dict)

        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v2", "v3"]):
            subscription.download(dry_run=False)

        with _mock_source(mock_downloaded_file_path, mock_entry_dict_factory, ["v1", "v2", "v3"]):
            transaction_log = subscription.download(dry_run=False)

        assert transaction_log.is_empty
        assert _archived_uids(output_directory) == ["v1", "v2", "v3"]
