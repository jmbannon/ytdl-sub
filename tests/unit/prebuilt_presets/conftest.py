import contextlib
import os
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import List
from unittest.mock import patch

import pytest
from resources import copy_file_fixture

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.downloaders.url.downloader import BaseUrlDownloader
from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.entries.variables.kwargs import DESCRIPTION
from ytdl_sub.entries.variables.kwargs import EPOCH
from ytdl_sub.entries.variables.kwargs import EXT
from ytdl_sub.entries.variables.kwargs import EXTRACTOR
from ytdl_sub.entries.variables.kwargs import PLAYLIST_COUNT
from ytdl_sub.entries.variables.kwargs import PLAYLIST_ENTRY
from ytdl_sub.entries.variables.kwargs import PLAYLIST_INDEX
from ytdl_sub.entries.variables.kwargs import TITLE
from ytdl_sub.entries.variables.kwargs import UID
from ytdl_sub.entries.variables.kwargs import UPLOAD_DATE
from ytdl_sub.entries.variables.kwargs import WEBPAGE_URL


@pytest.fixture
def subscription_name(working_directory) -> str:
    name = "subscription_test"
    os.makedirs(Path(working_directory) / name, exist_ok=True)
    return name


@pytest.fixture
def config(working_directory) -> ConfigFile:
    return ConfigFile(
        name="config",
        value={"configuration": {"working_directory": working_directory}, "presets": {}},
    )


@pytest.fixture
def mock_downloaded_file_path(working_directory: str, subscription_name: str):
    def _mock_downloaded_file_path(file_name: str) -> Path:
        return Path(working_directory) / subscription_name / file_name

    return _mock_downloaded_file_path


@pytest.fixture
def mock_entry_dict_factory(mock_downloaded_file_path) -> Callable:
    def _mock_entry_dict_factory(
        uid: int,
        upload_date: str,
        playlist_index: int = 1,
        playlist_count: int = 1,
        is_youtube_channel: bool = False,
        mock_download_to_working_dir: bool = True,
    ) -> Dict:
        entry_dict = {
            UID: uid,
            EPOCH: 1596878400,
            PLAYLIST_INDEX: playlist_index,
            PLAYLIST_COUNT: playlist_count,
            EXTRACTOR: "mock-entry-dict",
            TITLE: f"Mock Entry {uid}",
            EXT: "mp4",
            UPLOAD_DATE: upload_date,
            WEBPAGE_URL: f"https://{uid}.com",
            PLAYLIST_ENTRY: {"thumbnails": []},
            DESCRIPTION: "The Description",
        }

        if is_youtube_channel:
            entry_dict[PLAYLIST_ENTRY]["thumbnails"] = [
                {
                    "id": "avatar_uncropped",
                    "url": "https://avatar_uncropped.com",
                },
                {
                    "id": "banner_uncropped",
                    "url": "https://banner_uncropped.com",
                },
            ]

        # Create mock video file
        if mock_download_to_working_dir:
            copy_file_fixture(
                fixture_name="sample_vid.mp4",
                output_file_path=mock_downloaded_file_path(f"{uid}.mp4"),
            )
            copy_file_fixture(
                fixture_name="thumb.jpg", output_file_path=mock_downloaded_file_path(f"{uid}.jpg")
            )
        return entry_dict

    return _mock_entry_dict_factory


@pytest.fixture
def mock_download_collection_thumbnail(mock_downloaded_file_path):
    def _mock_download_and_convert_url_thumbnail(
        thumbnail_url: str, output_thumbnail_path: str
    ) -> bool:
        _ = thumbnail_url
        output_name = os.path.basename(output_thumbnail_path)
        if "poster" in output_name or "show" in output_name:
            copy_file_fixture(fixture_name="poster.jpg", output_file_path=output_thumbnail_path)
            return True
        elif "fanart" in output_name:
            copy_file_fixture(fixture_name="fanart.jpeg", output_file_path=output_thumbnail_path)
            return True
        return False

    with patch(
        "ytdl_sub.downloaders.url.downloader.download_and_convert_url_thumbnail",
        new=_mock_download_and_convert_url_thumbnail,
    ):
        yield  # TODO: create file here


@pytest.fixture
def mock_download_collection_entries(
    mock_download_collection_thumbnail, mock_entry_dict_factory: Callable, working_directory: str
):
    @contextlib.contextmanager
    def _mock_download_collection_entries_factory(is_youtube_channel: bool, num_urls: int = 1):
        def _write_entries_to_working_dir(*args, **kwargs) -> List[Dict]:
            if num_urls == 1 or ("2" in kwargs["url"] and num_urls > 1):
                return [
                    mock_entry_dict_factory(
                        uid="21-1",
                        upload_date="20210808",
                        playlist_index=1,
                        playlist_count=4,
                        is_youtube_channel=is_youtube_channel,
                    ),  # 1
                    mock_entry_dict_factory(
                        uid="20-1",
                        upload_date="20200808",
                        playlist_index=2,
                        playlist_count=4,
                        is_youtube_channel=is_youtube_channel,
                    ),  # 2  98
                    mock_entry_dict_factory(
                        uid="20-2",
                        upload_date="20200808",
                        playlist_index=3,
                        playlist_count=4,
                        is_youtube_channel=is_youtube_channel,
                    ),  # 1  99
                    mock_entry_dict_factory(
                        uid="20-3",
                        upload_date="20200807",
                        playlist_index=4,
                        playlist_count=4,
                        is_youtube_channel=is_youtube_channel,
                    ),
                ]
            return [
                # 20-3 should resolve to collection 1 (which is season 2)
                mock_entry_dict_factory(
                    uid="20-3",
                    upload_date="20200807",
                    playlist_index=1,
                    playlist_count=5,
                    is_youtube_channel=is_youtube_channel,
                    mock_download_to_working_dir=False,
                ),
                mock_entry_dict_factory(
                    uid="20-4",
                    upload_date="20200806",
                    playlist_index=2,
                    playlist_count=5,
                    is_youtube_channel=is_youtube_channel,
                ),
                mock_entry_dict_factory(
                    uid="20-5",
                    upload_date="20200706",
                    playlist_index=3,
                    playlist_count=5,
                    is_youtube_channel=is_youtube_channel,
                ),
                mock_entry_dict_factory(
                    uid="20-6",
                    upload_date="20200706",
                    playlist_index=4,
                    playlist_count=5,
                    is_youtube_channel=is_youtube_channel,
                ),
                mock_entry_dict_factory(
                    uid="20-7",
                    upload_date="20200606",
                    playlist_index=5,
                    playlist_count=5,
                    is_youtube_channel=is_youtube_channel,
                ),
            ]

        with patch.object(
            YTDLP, "extract_info_via_info_json", new=_write_entries_to_working_dir
        ), patch.object(
            BaseUrlDownloader, "_extract_entry_info_with_retry", new=lambda _, entry: entry
        ):
            # Stub out metadata. TODO: update this if we do metadata plugins
            yield

    return _mock_download_collection_entries_factory
