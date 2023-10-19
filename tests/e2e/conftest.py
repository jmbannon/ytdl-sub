import json
import sys
import tempfile
from typing import List
from typing import Tuple
from unittest.mock import patch

import pytest

from ytdl_sub.cli.entrypoint import main
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog


@pytest.fixture()
def music_video_config_for_cli(music_video_config) -> str:
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tmp_file:
        tmp_file.write(json.dumps(music_video_config._value).encode("utf-8"))

    try:
        yield tmp_file.name
    finally:
        FileHandler.delete(tmp_file.name)


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

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".txt", delete=False
    ) as tmp:
        tmp.writelines(timestamps)

    try:
        yield tmp.name
    finally:
        FileHandler.delete(tmp.name)


def mock_run_from_cli(args: str) -> List[Tuple[Subscription, FileHandlerTransactionLog]]:
    args_list = ["ytdl-sub"] + args.split()
    with patch.object(sys, "argv", args_list):
        return main()
