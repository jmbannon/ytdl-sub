import json
import sys
import tempfile
from typing import List
from unittest.mock import patch

import pytest

from ytdl_sub.cli.entrypoint import main
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.file_handler import FileHandler


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


def mock_run_from_cli(args: str) -> List[Subscription]:
    args_list = ["ytdl-sub"] + args.split()
    with patch.object(sys, "argv", args_list):
        return main()
