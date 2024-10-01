import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
from unittest.mock import patch

import pytest
from conftest import assert_logs

from ytdl_sub.cli.entrypoint import main
from ytdl_sub.cli.output_transaction_log import logger as transaction_logger
from ytdl_sub.utils.file_handler import FileHandler


@pytest.fixture
def transaction_log_file_path() -> str:
    # Delete the temp_file on creation
    with tempfile.NamedTemporaryFile() as temp_file:
        pass

    yield temp_file.name

    if os.path.isfile(temp_file.name):
        FileHandler.delete(temp_file.name)


@pytest.mark.parametrize("file_transaction_log", [None, "output.log"])
def test_suppress_transaction_log(
    mock_subscription_download_success,
    default_config_path: Path,
    music_video_subscription_path: Path,
    file_transaction_log: Optional[str],
) -> None:
    with (
        patch.object(
            sys,
            "argv",
            [
                "ytdl-sub",
                "--config",
                str(default_config_path),
                "sub",
                str(music_video_subscription_path),
                "--suppress-transaction-log",
            ]
            + (["--transaction-log", file_transaction_log] if file_transaction_log else []),
        ),
        patch("ytdl_sub.cli.output_transaction_log.output_transaction_log") as mock_transaction_log,
    ):
        subscriptions = main()

        assert subscriptions
        assert mock_transaction_log.call_count == 0


def test_transaction_log_to_file(
    mock_subscription_download_success,
    default_config_path: Path,
    music_video_subscription_path: Path,
    transaction_log_file_path: Path,
) -> None:
    with patch.object(
        sys,
        "argv",
        [
            "ytdl-sub",
            "--config",
            str(default_config_path),
            "sub",
            str(music_video_subscription_path),
            "--transaction-log",
            str(transaction_log_file_path),
        ],
    ):
        subscriptions = main()
        assert subscriptions

    with open(transaction_log_file_path, "r", encoding="utf-8") as transaction_log_file:
        assert transaction_log_file.readlines()[0] == "Transaction log for Rick Astley:\n"


def test_transaction_log_to_logger(
    mock_subscription_download_success,
    default_config_path: Path,
    music_video_subscription_path: Path,
) -> None:
    with (
        patch.object(
            sys,
            "argv",
            [
                "ytdl-sub",
                "--config",
                str(default_config_path),
                "sub",
                str(music_video_subscription_path),
            ],
        ),
        assert_logs(
            logger=transaction_logger,
            expected_message="Transaction log for Rick Astley:\n",
            log_level="info",
        ),
    ):
        subscriptions = main()
        assert subscriptions
