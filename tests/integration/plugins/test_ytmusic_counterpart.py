import contextlib
import json
import os
from pathlib import Path
from typing import Callable, Dict, List, Optional
from unittest.mock import patch

import pytest
from resources import copy_file_fixture

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.downloaders.url.downloader import MultiUrlDownloader
from ytdl_sub.downloaders.url.ytmusic import YTMusicCounterpartResolver
from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.plugins.throttle_protection import ThrottleProtectionPlugin
from ytdl_sub.subscriptions.subscription import Subscription

ARCHIVE_FILE_NAME = ".ytdl-sub-subscription_test-download-archive.json"

# Maps the music video the source enumerates to its audio-only counterpart. 'video_only' has
# no song version, which is the case for video-only releases and non-music uploads.
COUNTERPARTS = {"video_1": "song_1", "video_2": "song_2", "video_only": None}


@pytest.fixture
def ytmusic_subscription_dict(output_directory: str) -> Dict:
    return {
        "download": {
            "urls": [
                {
                    "url": "https://music.youtube.com/playlist?list=LM",
                    "ytmusic_counterpart": "song",
                }
            ]
        },
        "output_options": {
            "output_directory": output_directory,
            "file_name": "{title_sanitized}.{ext}",
            "maintain_download_archive": True,
        },
    }


@contextlib.contextmanager
def _mock_source(
    mock_downloaded_file_path: Callable,
    mock_entry_dict_factory: Callable,
    uids: List[str],
    resolve_calls: Optional[List[str]] = None,
    archive_ids_seen: Optional[List[str]] = None,
):
    """
    Patches the inner ``extract_info`` so the real metadata collection runs, including
    yt-dlp's behavior of writing no info.json for an entry already in the download archive.
    The counterpart lookup is patched at the resolver so no InnerTube request is made, and
    fetching the counterpart's metadata returns a fresh entry dict for its own id.
    """

    def _extract_info(ytdl_options_overrides: Dict, **kwargs) -> Dict:
        archived_ids = set()
        archive_path = ytdl_options_overrides.get("download_archive")
        if archive_path and os.path.isfile(archive_path):
            with open(archive_path, "r", encoding="utf-8") as archive_file:
                archived_ids = {line.split()[-1] for line in archive_file if line.strip()}
            if archive_ids_seen is not None:
                archive_ids_seen.extend(sorted(archived_ids))

        # Fetching a single counterpart's metadata rather than enumerating the source
        url = kwargs.get("url", "")
        if "watch?v=" in url:
            return mock_entry_dict_factory(
                uid=url.split("watch?v=")[-1],
                upload_date="20210801",
                mock_download_to_working_dir=False,
                mock_entry_kwargs={"extractor_key": "Youtube"},
            )

        for idx, uid in enumerate(uids):
            if uid in archived_ids:
                continue

            entry_dict = mock_entry_dict_factory(
                uid=uid,
                upload_date=f"2021080{idx + 1}",
                playlist_index=idx + 1,
                playlist_count=len(uids),
                mock_download_to_working_dir=False,
                mock_entry_kwargs={"extractor_key": "Youtube"},
            )
            with open(
                mock_downloaded_file_path(f"{uid}.info.json"), "w", encoding="utf-8"
            ) as info_json_file:
                json.dump(entry_dict, info_json_file)

        return {}

    def _resolve(_, video_id: str, prefer: str) -> Optional[str]:
        assert prefer == "song"
        if resolve_calls is not None:
            resolve_calls.append(video_id)
        return COUNTERPARTS.get(video_id, video_id)

    def _mock_entry_download(_, entry):
        copy_file_fixture(
            fixture_name="sample_vid.mp4",
            output_file_path=mock_downloaded_file_path(f"{entry.uid}.mp4"),
        )
        return entry

    with (
        patch.object(YTDLP, "extract_info", new=_extract_info),
        patch.object(YTMusicCounterpartResolver, "resolve", new=_resolve),
        patch.object(
            MultiUrlDownloader, "_extract_entry_info_with_retry", new=_mock_entry_download
        ),
        patch.object(ThrottleProtectionPlugin, "perform_sleep", new=lambda _1, _2: None),
    ):
        yield


def _archive(output_directory: str) -> Dict:
    with open(Path(output_directory) / ARCHIVE_FILE_NAME, "r", encoding="utf-8") as archive_file:
        return json.load(archive_file)


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


class TestYTMusicCounterpart:
    def test_music_videos_are_downloaded_as_songs(
        self,
        config: ConfigFile,
        subscription_name: str,
        ytmusic_subscription_dict: Dict,
        output_directory: str,
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = _subscription(config, subscription_name, ytmusic_subscription_dict)

        with _mock_source(
            mock_downloaded_file_path, mock_entry_dict_factory, ["video_1", "video_2"]
        ):
            subscription.download(dry_run=False)

        # The archive and the file names describe the song that was actually downloaded
        archive = _archive(output_directory)
        assert sorted(archive.keys()) == ["song_1", "song_2"]
        assert _output_files(output_directory) == ["Mock Entry song_1.mp4", "Mock Entry song_2.mp4"]

        # The video the source enumerates is recorded, so it can be suppressed next run
        assert archive["song_1"]["source_uid"] == "video_1"
        assert archive["song_2"]["source_uid"] == "video_2"

    def test_second_run_downloads_nothing_and_resolves_nothing(
        self,
        config: ConfigFile,
        subscription_name: str,
        ytmusic_subscription_dict: Dict,
        output_directory: str,
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = _subscription(config, subscription_name, ytmusic_subscription_dict)

        with _mock_source(
            mock_downloaded_file_path, mock_entry_dict_factory, ["video_1", "video_2"]
        ):
            subscription.download(dry_run=False)

        resolve_calls: List[str] = []
        archive_ids_seen: List[str] = []
        with _mock_source(
            mock_downloaded_file_path,
            mock_entry_dict_factory,
            ["video_1", "video_2"],
            resolve_calls=resolve_calls,
            archive_ids_seen=archive_ids_seen,
        ):
            transaction_log = subscription.download(dry_run=False)

        # Both the song and the video it came from must reach yt-dlp's archive, otherwise the
        # source keeps enumerating videos it has never seen and every entry is re-resolved
        assert archive_ids_seen == ["song_1", "song_2", "video_1", "video_2"]
        assert transaction_log.is_empty
        assert resolve_calls == []
        assert sorted(_archive(output_directory).keys()) == ["song_1", "song_2"]
        assert _output_files(output_directory) == ["Mock Entry song_1.mp4", "Mock Entry song_2.mp4"]

    def test_entry_without_a_song_is_downloaded_as_is(
        self,
        config: ConfigFile,
        subscription_name: str,
        ytmusic_subscription_dict: Dict,
        output_directory: str,
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        subscription = _subscription(config, subscription_name, ytmusic_subscription_dict)

        with _mock_source(
            mock_downloaded_file_path, mock_entry_dict_factory, ["video_1", "video_only"]
        ):
            subscription.download(dry_run=False)

        assert sorted(_archive(output_directory).keys()) == ["song_1", "video_only"]
        assert _output_files(output_directory) == [
            "Mock Entry song_1.mp4",
            "Mock Entry video_only.mp4",
        ]

    def test_entry_without_a_song_is_skipped_when_configured(
        self,
        config: ConfigFile,
        subscription_name: str,
        ytmusic_subscription_dict: Dict,
        output_directory: str,
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        url_options = ytmusic_subscription_dict["download"]["urls"][0]
        url_options["ytmusic_counterpart_when_missing"] = "skip"
        subscription = _subscription(config, subscription_name, ytmusic_subscription_dict)

        with _mock_source(
            mock_downloaded_file_path, mock_entry_dict_factory, ["video_1", "video_only"]
        ):
            subscription.download(dry_run=False)

        assert sorted(_archive(output_directory).keys()) == ["song_1"]
        assert _output_files(output_directory) == ["Mock Entry song_1.mp4"]

    def test_disabled_by_default_downloads_the_music_video(
        self,
        config: ConfigFile,
        subscription_name: str,
        ytmusic_subscription_dict: Dict,
        output_directory: str,
        mock_downloaded_file_path: Callable,
        mock_entry_dict_factory: Callable,
        mock_download_collection_thumbnail,
    ):
        del ytmusic_subscription_dict["download"]["urls"][0]["ytmusic_counterpart"]
        subscription = _subscription(config, subscription_name, ytmusic_subscription_dict)

        resolve_calls: List[str] = []
        with _mock_source(
            mock_downloaded_file_path,
            mock_entry_dict_factory,
            ["video_1", "video_2"],
            resolve_calls=resolve_calls,
        ):
            subscription.download(dry_run=False)

        assert resolve_calls == []
        assert sorted(_archive(output_directory).keys()) == ["video_1", "video_2"]
        assert "source_uid" not in _archive(output_directory)["video_1"]
