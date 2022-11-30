import json
import shutil
import sys
import tempfile
from typing import List
from typing import Tuple
from unittest.mock import patch

import pytest
from expected_download import _get_files_in_directory

from ytdl_sub.cli.main import main
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.subscriptions.subscription_download import SubscriptionDownload
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.yaml import load_yaml

logger = Logger.get("test")


@pytest.fixture
def working_directory() -> str:
    """
    Any time the working directory is used, ensure no files remain on cleaning it up
    """
    with tempfile.TemporaryDirectory() as temp_dir:

        def _assert_working_directory_empty(self, is_error: bool = False):
            files = [str(file_path) for file_path in _get_files_in_directory(temp_dir)]
            num_files = len(files)
            shutil.rmtree(temp_dir)

            if not is_error:
                if num_files > 0:
                    logger.error("left-over files in working dir:\n%s", "\n".join(files))
                assert num_files == 0

        with patch.object(
            SubscriptionDownload,
            "_delete_working_directory",
            new=_assert_working_directory_empty,
        ):
            yield temp_dir


@pytest.fixture()
def music_video_config_path():
    return "examples/music_videos_config.yaml"


def _load_config(config_path: str, working_directory: str) -> ConfigFile:
    config_dict = load_yaml(file_path=config_path)
    config_dict["configuration"]["working_directory"] = working_directory

    return ConfigFile.from_dict(config_dict)


@pytest.fixture()
def music_video_config(music_video_config_path, working_directory) -> ConfigFile:
    return _load_config(music_video_config_path, working_directory)


@pytest.fixture()
def music_video_config_for_cli(music_video_config) -> str:
    with tempfile.NamedTemporaryFile(suffix=".yaml") as tmp_file:
        tmp_file.write(json.dumps(music_video_config._value).encode("utf-8"))
        tmp_file.flush()
        yield tmp_file.name


@pytest.fixture()
def channel_as_tv_show_config(working_directory) -> ConfigFile:
    return _load_config(
        config_path="examples/tv_show_config.yaml", working_directory=working_directory
    )


@pytest.fixture
def soundcloud_discography_config(working_directory) -> ConfigFile:
    return _load_config(
        config_path="examples/soundcloud_discography_config.yaml",
        working_directory=working_directory,
    )


@pytest.fixture()
def youtube_audio_config(working_directory) -> ConfigFile:
    return _load_config(
        config_path="examples/music_audio_from_videos.yaml", working_directory=working_directory
    )


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
