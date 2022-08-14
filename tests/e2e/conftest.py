import sys
import tempfile
from typing import List
from typing import Tuple
from unittest.mock import patch

import pytest

from ytdl_sub.cli.main import main
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog


@pytest.fixture()
def output_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture()
def music_video_config_path():
    return "examples/kodi_music_videos_config.yaml"


@pytest.fixture()
def music_video_config(music_video_config_path):
    return ConfigFile.from_file_path(config_path=music_video_config_path)


@pytest.fixture()
def channel_as_tv_show_config():
    return ConfigFile.from_file_path(config_path="examples/kodi_tv_shows_config.yaml")


@pytest.fixture
def soundcloud_discography_config():
    return ConfigFile.from_file_path(config_path="examples/soundcloud_discography_config.yaml")


@pytest.fixture()
def youtube_audio_config_path():
    return "examples/youtube_extract_and_tag_audio.yaml"


@pytest.fixture()
def youtube_audio_config(youtube_audio_config_path):
    return ConfigFile.from_file_path(config_path=youtube_audio_config_path)


@pytest.fixture
def timestamps_file_path():
    timestamps = [
        "0:00 Intro\n",
        "00:10 Part 1\n",
        "0:20 Part 2\n",
        "00:30 Part 3\n",
        "0:00:40 Part 4\n",
        "00:01:01 Part 5\n",
    ]

    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".txt") as tmp:
        tmp.writelines(timestamps)
        tmp.seek(0)
        yield tmp.name


def mock_run_from_cli(args: str) -> List[Tuple[Subscription, FileHandlerTransactionLog]]:
    args_list = ["ytdl-sub"] + args.split()
    with patch.object(sys, "argv", args_list):
        return main()
