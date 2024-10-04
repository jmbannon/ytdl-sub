import contextlib
import os
import shutil
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import List
from unittest.mock import patch

import pytest
from resources import copy_file_fixture

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.downloaders.url.downloader import MultiUrlDownloader
from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions

v: VariableDefinitions = VARIABLES


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
        playlist_title: str = "playlist title",
        playlist_index: int = 1,
        playlist_count: int = 1,
        is_youtube_channel: bool = False,
        mock_download_to_working_dir: bool = True,
        is_extracted_audio: bool = False,
    ) -> Dict:
        entry_dict = {
            v.uid.metadata_key: uid,
            v.epoch.metadata_key: 1596878400,
            v.duration.metadata_key: 42 if is_extracted_audio else 31,
            v.playlist_title.metadata_key: playlist_title,
            v.playlist_index.metadata_key: playlist_index,
            v.playlist_count.metadata_key: playlist_count,
            v.extractor.metadata_key: "mock-entry-extractor",
            v.extractor_key.metadata_key: "mock-entry-dict",
            v.title.metadata_key: f"Mock Entry {uid}",
            v.ext.metadata_key: "mp4",
            v.upload_date.metadata_key: upload_date,
            v.webpage_url.metadata_key: f"https://{uid}.com",
            v.playlist_metadata.metadata_key: {"thumbnails": []},
            v.description.metadata_key: "The Description",
        }

        if is_youtube_channel:
            entry_dict[v.playlist_metadata.metadata_key]["thumbnails"] = [
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
            if is_extracted_audio:
                copy_file_fixture(
                    fixture_name="sample_audio.mp3",
                    output_file_path=mock_downloaded_file_path(f"{uid}.mp3"),
                )
            else:
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
            copy_file_fixture(
                fixture_name="poster.jpg", output_file_path=Path(output_thumbnail_path)
            )
            return True
        elif "fanart" in output_name:
            copy_file_fixture(
                fixture_name="fanart.jpeg", output_file_path=Path(output_thumbnail_path)
            )
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
    def _mock_download_collection_entries_factory(
        is_youtube_channel: bool,
        num_urls: int = 1,
        is_extracted_audio: bool = False,
        is_dry_run: bool = False,
    ):
        is_real_run = not is_dry_run

        def _write_entries_to_working_dir(*args, **kwargs) -> List[Dict]:
            # Second TV URL or second soundcloud URL, which downloads first
            is_second_url = "2" in kwargs["url"] or kwargs["url"].endswith("/albums")

            if num_urls == 0:
                return []
            if num_urls == 1 or (is_second_url and num_urls > 1):
                return [
                    mock_entry_dict_factory(
                        uid="21-1",
                        upload_date="20210808",
                        playlist_title="Download First",
                        playlist_index=1,
                        playlist_count=4,
                        is_youtube_channel=is_youtube_channel,
                        is_extracted_audio=is_extracted_audio,
                        mock_download_to_working_dir=is_real_run,
                    ),  # 1
                    mock_entry_dict_factory(
                        uid="20-1",
                        upload_date="20200808",
                        playlist_title="Download First",
                        playlist_index=2,
                        playlist_count=4,
                        is_youtube_channel=is_youtube_channel,
                        is_extracted_audio=is_extracted_audio,
                        mock_download_to_working_dir=is_real_run,
                    ),  # 2  98
                    mock_entry_dict_factory(
                        uid="20-2",
                        upload_date="20200808",
                        playlist_title="Download First",
                        playlist_index=3,
                        playlist_count=4,
                        is_youtube_channel=is_youtube_channel,
                        is_extracted_audio=is_extracted_audio,
                        mock_download_to_working_dir=is_real_run,
                    ),  # 1  99
                    mock_entry_dict_factory(
                        uid="20-3",
                        upload_date="20200807",
                        playlist_title="Download First",
                        playlist_index=4,
                        playlist_count=4,
                        is_youtube_channel=is_youtube_channel,
                        is_extracted_audio=is_extracted_audio,
                        mock_download_to_working_dir=is_real_run,
                    ),
                ]
            return [
                # 20-3 should resolve to collection 1 (which is season 2)
                mock_entry_dict_factory(
                    uid="20-3",
                    upload_date="20200807",
                    playlist_title="Download Second",
                    playlist_index=1,
                    playlist_count=5,
                    is_youtube_channel=is_youtube_channel,
                    is_extracted_audio=is_extracted_audio,
                    mock_download_to_working_dir=False,
                ),
                mock_entry_dict_factory(
                    uid="20-4",
                    upload_date="20200806",
                    playlist_title="Download Second",
                    playlist_index=2,
                    playlist_count=5,
                    is_youtube_channel=is_youtube_channel,
                    is_extracted_audio=is_extracted_audio,
                    mock_download_to_working_dir=is_real_run,
                ),
                mock_entry_dict_factory(
                    uid="20-5",
                    upload_date="20200706",
                    playlist_title="Download Second",
                    playlist_index=3,
                    playlist_count=5,
                    is_youtube_channel=is_youtube_channel,
                    is_extracted_audio=is_extracted_audio,
                    mock_download_to_working_dir=is_real_run,
                ),
                mock_entry_dict_factory(
                    uid="20-6",
                    upload_date="20200706",
                    playlist_title="Download Second",
                    playlist_index=4,
                    playlist_count=5,
                    is_youtube_channel=is_youtube_channel,
                    is_extracted_audio=is_extracted_audio,
                    mock_download_to_working_dir=is_real_run,
                ),
                mock_entry_dict_factory(
                    uid="20-7",
                    upload_date="20200606",
                    playlist_title="Download Second",
                    playlist_index=5,
                    playlist_count=5,
                    is_youtube_channel=is_youtube_channel,
                    is_extracted_audio=is_extracted_audio,
                    mock_download_to_working_dir=is_real_run,
                ),
            ]

        with (
            patch.object(YTDLP, "extract_info_via_info_json", new=_write_entries_to_working_dir),
            patch.object(
                MultiUrlDownloader, "_extract_entry_info_with_retry", new=lambda _, entry: entry
            ),
        ):
            # Stub out metadata. TODO: update this if we do metadata plugins
            yield

    return _mock_download_collection_entries_factory
