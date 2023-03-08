import sys
import tempfile
from unittest.mock import patch

import pytest

from ytdl_sub.cli.main import main


def test_args_after_sub_work():
    with patch.object(
        sys,
        "argv",
        ["ytdl-sub", "-c", "examples/tv_show_config.yaml", "sub", "--log-level", "debug"],
    ), patch("ytdl_sub.cli.main._download_subscriptions_from_yaml_files") as mock_sub:
        main()

        assert mock_sub.call_count == 1
        assert mock_sub.call_args.kwargs["args"].config == "examples/tv_show_config.yaml"
        assert mock_sub.call_args.kwargs["args"].subscription_paths == ["subscriptions.yaml"]
        assert mock_sub.call_args.kwargs["args"].ytdl_sub_log_level == "debug"


@pytest.fixture
def persist_logs_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def persist_logs_config():
    pass


class TestPersistLogs:
    @pytest.mark.parametrize("mock_success_output", [True, False])
    @pytest.mark.parametrize("keep_successful_logs", [True, False])
    def test_subscription_logs_write_to_file(
        self, persist_logs_directory: str, mock_success_output: bool, keep_successful_logs: bool
    ):

        config_dict = {
            "working_directory": ".",
            "persist_logs": {
                "logs_directory": persist_logs_directory,
                "keep_successful_logs": keep_successful_logs,
            },
        }
