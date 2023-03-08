import os.path
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Callable
from unittest.mock import patch

import mergedeep
import pytest

from ytdl_sub.cli.main import _download_subscriptions_from_yaml_files
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog
from ytdl_sub.utils.logger import Logger


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
            return FileHandlerTransactionLog()

        return _mock_download

    return _mock_subscription_download_factory


class TestPersistLogs:
    @pytest.mark.parametrize("dry_run", [True, False])
    @pytest.mark.parametrize("mock_success_output", [True, False])
    @pytest.mark.parametrize("keep_successful_logs", [True, False])
    def test_subscription_logs_write_to_file(
        self,
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
                    config=config, subscription_paths=subscription_paths, dry_run=dry_run
                )
            except ValueError:
                assert not mock_success_output

        log_directory_files = list(Path(persist_logs_directory).rglob("*"))

        # If dry run or success but success logging disabled, expect 0 log files
        if dry_run or (mock_success_output and not keep_successful_logs):
            assert len(log_directory_files) == 0
            return
        # If not success, expect 1 log file
        elif not mock_success_output:
            assert len(log_directory_files) == 1
            log_path = log_directory_files[0]
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
                    re.match(
                        r"\d{4}-\d{2}-\d{2}-\d{6}\.john_smith\.success\.log", log_file_path.name
                    )
                )
                with open(log_file_path, "r", encoding="utf-8") as log_file:
                    assert (
                        log_file.readlines()[-1]
                        == "[ytdl-sub] name=john_smith success=True dry_run=False\n"
                    )
