import datetime
import os
import shutil
import tempfile
import time
from typing import Callable
from unittest.mock import patch

import mergedeep
import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger


@pytest.fixture
def mock_subscription_download_factory():
    def _mock_subscription_download_factory(mock_success_output: bool) -> Callable:
        def _mock_download(self: Subscription, dry_run: bool) -> FileHandlerTransactionLog:
            Logger.get().info(
                "name=%s success=%s dry_run=%s", self.name, mock_success_output, dry_run
            )

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
    default_config: ConfigFile, persist_logs_directory: str
) -> Callable:
    def _persist_logs_config_factory(keep_successful_logs: bool) -> ConfigFile:
        return ConfigFile.from_dict(
            dict(
                mergedeep.merge(
                    default_config.as_dict(),
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
