import os.path
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import mergedeep
import pytest
from conftest import assert_logs

from ytdl_sub.cli.entrypoint import _download_subscriptions_from_yaml_files
from ytdl_sub.cli.entrypoint import main
from ytdl_sub.cli.output_summary import output_summary
from ytdl_sub.cli.output_transaction_log import logger as transaction_logger
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ExperimentalFeatureNotEnabled
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger

####################################################################################################
# SHARED FIXTURES


@pytest.fixture
def mock_subscription_download_factory():
    def _mock_subscription_download_factory(mock_success_output: bool) -> Callable:
        def _mock_download(self: Subscription, dry_run: bool) -> FileHandlerTransactionLog:
            Logger.get().info(
                "name=%s success=%s dry_run=%s", self.name, mock_success_output, dry_run
            )
            time.sleep(1)
            if not mock_success_output:
                raise ValueError("error")

            (
                self._enhanced_download_archive.get_file_handler_transaction_log()
                .log_created_file("created_file.txt", FileMetadata())
                .log_modified_file("modified_file.txt", FileMetadata())
                .log_removed_file("deleted_file.txt")
            )

            return self._enhanced_download_archive.get_file_handler_transaction_log()

        return _mock_download

    return _mock_subscription_download_factory


@pytest.fixture
def mock_subscription_download_success(mock_subscription_download_factory: Callable):
    with patch.object(
        Subscription,
        "download",
        new=mock_subscription_download_factory(mock_success_output=True),
    ):
        yield


####################################################################################################
# PERSIST LOGS FIXTURES + TESTS


@pytest.fixture
def persist_logs_directory() -> str:
    # Delete the temp_dir on creation
    with tempfile.TemporaryDirectory() as temp_dir:
        pass

    yield temp_dir

    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def persist_logs_config_factory(
    music_video_config: ConfigFile, persist_logs_directory: str
) -> Callable:
    def _persist_logs_config_factory(keep_successful_logs: bool) -> ConfigFile:
        return ConfigFile.from_dict(
            dict(
                mergedeep.merge(
                    music_video_config.as_dict(),
                    {
                        "configuration": {
                            "persist_logs": {
                                "logs_directory": persist_logs_directory,
                                "keep_successful_logs": keep_successful_logs,
                            },
                        }
                    },
                )
            )
        )

    return _persist_logs_config_factory


@pytest.mark.parametrize("dry_run", [True, False])
@pytest.mark.parametrize("mock_success_output", [True, False])
@pytest.mark.parametrize("keep_successful_logs", [True, False])
def test_subscription_logs_write_to_file(
    persist_logs_directory: str,
    persist_logs_config_factory: Callable,
    mock_subscription_download_factory: Callable,
    music_video_subscription_path: Path,
    dry_run: bool,
    mock_success_output: bool,
    keep_successful_logs: bool,
):
    num_subscriptions = 2
    config = persist_logs_config_factory(keep_successful_logs=keep_successful_logs)
    subscription_paths = [str(music_video_subscription_path)] * num_subscriptions

    with patch.object(
        Subscription,
        "download",
        new=mock_subscription_download_factory(mock_success_output=mock_success_output),
    ):
        try:
            _download_subscriptions_from_yaml_files(
                config=config,
                subscription_paths=subscription_paths,
                update_with_info_json=False,
                dry_run=dry_run,
            )
        except ValueError:
            assert not mock_success_output

    log_directory_files = list(Path(persist_logs_directory).rglob("*"))

    # If dry run or success but success logging disabled, expect 0 log files
    if dry_run or (mock_success_output and not keep_successful_logs):
        assert len(log_directory_files) == 0
        return
    # If not success, expect 2 log files for both sub errors
    elif not mock_success_output:
        assert len(log_directory_files) == 2
        for log_path in log_directory_files:
            assert bool(re.match(r"\d{4}-\d{2}-\d{2}-\d{6}\.john_smith\.error\.log", log_path.name))
            with open(log_path, "r", encoding="utf-8") as log_file:
                assert log_file.readlines()[-1] == (
                    f"Please upload the error log file '{str(log_path)}' and make a Github issue "
                    f"at https://github.com/jmbannon/ytdl-sub/issues with your config and "
                    f"command/subscription yaml file to reproduce. Thanks for trying ytdl-sub!\n"
                )
    # If success and success logging, expect 3 log files
    else:
        assert len(log_directory_files) == num_subscriptions
        for log_file_path in log_directory_files:
            assert bool(
                re.match(r"\d{4}-\d{2}-\d{2}-\d{6}\.john_smith\.success\.log", log_file_path.name)
            )
            with open(log_file_path, "r", encoding="utf-8") as log_file:
                assert (
                    log_file.readlines()[-1]
                    == "[ytdl-sub] name=john_smith success=True dry_run=False\n"
                )


####################################################################################################
# TRANSACTION LOGS FIXTURES + TESTS


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
    music_video_config_path: Path,
    music_video_subscription_path: Path,
    file_transaction_log: Optional[str],
) -> None:
    with patch.object(
        sys,
        "argv",
        [
            "ytdl-sub",
            "--config",
            str(music_video_config_path),
            "sub",
            str(music_video_subscription_path),
            "--suppress-transaction-log",
        ]
        + (["--transaction-log", file_transaction_log] if file_transaction_log else []),
    ), patch("ytdl_sub.cli.output_transaction_log.output_transaction_log") as mock_transaction_log:
        transaction_logs = main()

        assert transaction_logs
        assert mock_transaction_log.call_count == 0


def test_transaction_log_to_file(
    mock_subscription_download_success,
    music_video_config_path: Path,
    music_video_subscription_path: Path,
    transaction_log_file_path: Path,
) -> None:
    with patch.object(
        sys,
        "argv",
        [
            "ytdl-sub",
            "--config",
            str(music_video_config_path),
            "sub",
            str(music_video_subscription_path),
            "--transaction-log",
            str(transaction_log_file_path),
        ],
    ):
        subscriptions = main()
        assert subscriptions

    with open(transaction_log_file_path, "r", encoding="utf-8") as transaction_log_file:
        assert transaction_log_file.readlines()[0] == "Transaction log for john_smith:\n"


def test_transaction_log_to_logger(
    mock_subscription_download_success,
    music_video_config_path: Path,
    music_video_subscription_path: Path,
) -> None:
    with patch.object(
        sys,
        "argv",
        [
            "ytdl-sub",
            "--config",
            str(music_video_config_path),
            "sub",
            str(music_video_subscription_path),
        ],
    ), assert_logs(
        logger=transaction_logger,
        expected_message="Transaction log for john_smith:\n",
        log_level="info",
    ):
        transaction_logs = main()
        assert transaction_logs


def test_output_summary():
    subscription_values: List[Tuple[str, int, int, int, int, Optional[Exception]]] = [
        ("long_name_but_lil_values", 0, 0, 0, 6, None),
        ("john_smith", 1, 0, 0, 52, None),
        ("david_gore", 0, 0, 0, 4, None),
        ("christopher_snoop", 50, 0, 3, 518, None),
        ("beyond funk", 0, 0, 0, 176, ValueError("lol")),
    ]

    mock_subscriptions: List[MagicMock] = []
    for values in subscription_values:
        sub = Mock()
        sub.name = values[0]
        sub.num_entries_added = values[1]
        sub.num_entries_modified = values[2]
        sub.num_entries_removed = values[3]
        sub.num_entries = values[4]
        sub.exception = values[5]

        mock_subscriptions.append(sub)

    _ = output_summary(subscriptions=mock_subscriptions)
    assert True  # Test used for manual inspection - too hard to test ansi color codes


def test_update_with_info_json_requires_experimental_flag(
    music_video_config_path: Path,
    music_video_subscription_path: Path,
) -> None:
    with patch.object(
        sys,
        "argv",
        [
            "ytdl-sub",
            "--config",
            str(music_video_config_path),
            "sub",
            str(music_video_subscription_path),
            "--update-with-info-json",
        ],
    ), pytest.raises(ExperimentalFeatureNotEnabled):
        _ = main()
