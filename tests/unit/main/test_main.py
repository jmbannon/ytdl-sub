import contextlib
import logging
import os.path
import sys
from unittest.mock import patch

import pytest

from src.ytdl_sub import __local_version__
from src.ytdl_sub.main import main
from ytdl_sub.cli.parsers.main import DEFAULT_CONFIG_FILE_NAME
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.logger import LoggerLevels


@pytest.fixture
def expected_uncaught_error_message():
    return (
        f"Version %s\nPlease upload the error log file '%s' and make a "
        f"Github issue at https://github.com/jmbannon/ytdl-sub/issues with your config and "
        f"command/subscription yaml file to reproduce. Thanks for trying ytdl-sub!"
    )


@pytest.fixture
def mock_sys_exit():
    @contextlib.contextmanager
    def _mock_sys_exit(expected_exit_code: int):
        with patch.object(sys, "exit") as mock_exit:
            yield mock_exit

        assert mock_exit.called
        assert mock_exit.call_args_list[0].args[0] == expected_exit_code

    return _mock_sys_exit


@pytest.mark.parametrize("return_code", [0, 1])
def test_main_exit_code(mock_sys_exit, return_code: int):
    with mock_sys_exit(expected_exit_code=return_code), patch(
        "src.ytdl_sub.main._main"
    ) as mock_inner_main, patch.object(Logger, "cleanup") as mock_logger_cleanup:
        mock_inner_main.return_value = return_code
        main()

        assert mock_logger_cleanup.call_count == 1
        assert mock_logger_cleanup.call_args.kwargs["has_error"] == (
            True if return_code != 0 else False
        )


def test_main_validation_error(capsys, mock_sys_exit):
    validation_exception = ValidationException("test exc")
    with mock_sys_exit(expected_exit_code=1), patch(
        "src.ytdl_sub.main._main", side_effect=validation_exception
    ), patch.object(logging.Logger, "error") as mock_logger:
        main()

    assert mock_logger.call_count == 1
    assert mock_logger.call_args.args[0] == "test exc"


def test_main_uncaught_error(capsys, mock_sys_exit, expected_uncaught_error_message):
    uncaught_error = ValueError("test")
    with mock_sys_exit(expected_exit_code=1), patch(
        "src.ytdl_sub.main._main", side_effect=uncaught_error
    ), patch.object(logging.Logger, "exception") as mock_exception, patch.object(
        logging.Logger, "error"
    ) as mock_error:
        main()

    assert mock_exception.call_count == 1
    assert mock_exception.call_args.args[0] == "An uncaught error occurred:"

    assert mock_error.call_count == 1
    assert mock_error.call_args.args[0] == expected_uncaught_error_message
    assert mock_error.call_args.args[1] == __local_version__
    assert mock_error.call_args.args[2] == Logger.error_log_filename()


def test_main_permission_error(capsys, mock_sys_exit, expected_uncaught_error_message):
    permission_error = PermissionError("test")
    with mock_sys_exit(expected_exit_code=1), patch(
        "src.ytdl_sub.main._main", side_effect=permission_error
    ), patch.object(logging.Logger, "error") as mock_error:
        main()

    assert mock_error.call_count == 1
    assert mock_error.call_args.args[0] == (
        "A permission error occurred:\n%s\n"
        "The user running ytdl-sub must have permission to this file/directory."
    )
    assert mock_error.call_args.args[1] == "test"


def test_args_after_sub_work(mock_sys_exit, tv_show_config_path):
    with mock_sys_exit(expected_exit_code=0), patch.object(
        sys,
        "argv",
        ["ytdl-sub", "-c", tv_show_config_path, "sub", "--log-level", "verbose"],
    ), patch("ytdl_sub.cli.entrypoint._download_subscriptions_from_yaml_files") as mock_sub:
        main()

        assert mock_sub.call_count == 1
        assert mock_sub.call_args.kwargs["subscription_paths"] == ["subscriptions.yaml"]
        assert mock_sub.call_args.kwargs["config"]._name == tv_show_config_path
        assert mock_sub.call_args.kwargs["subscription_matches"] == []
        assert Logger._LOGGER_LEVEL == LoggerLevels.VERBOSE


def test_sub_match_arguments_before(mock_sys_exit, tv_show_config_path):
    with mock_sys_exit(expected_exit_code=0), patch.object(
        sys,
        "argv",
        [
            "ytdl-sub",
            "--match",
            "testA",
            "testB",
            "-c",
            tv_show_config_path,
            "sub",
            "--log-level",
            "verbose",
        ],
    ), patch("ytdl_sub.cli.entrypoint._download_subscriptions_from_yaml_files") as mock_sub:
        main()

        assert mock_sub.call_count == 1
        assert mock_sub.call_args.kwargs["subscription_paths"] == ["subscriptions.yaml"]
        assert mock_sub.call_args.kwargs["config"]._name == tv_show_config_path
        assert mock_sub.call_args.kwargs["subscription_matches"] == ["testA", "testB"]
        assert Logger._LOGGER_LEVEL == LoggerLevels.VERBOSE


def test_sub_match_arguments_after_many(mock_sys_exit, tv_show_config_path):
    with mock_sys_exit(expected_exit_code=0), patch.object(
        sys,
        "argv",
        [
            "ytdl-sub",
            "-c",
            tv_show_config_path,
            "sub",
            "--log-level",
            "verbose",
            "--match",
            "testA",
            "--match",
            "testB",
        ],
    ), patch("ytdl_sub.cli.entrypoint._download_subscriptions_from_yaml_files") as mock_sub:
        main()

        assert mock_sub.call_count == 1
        assert mock_sub.call_args.kwargs["subscription_paths"] == ["subscriptions.yaml"]
        assert mock_sub.call_args.kwargs["config"]._name == tv_show_config_path
        assert mock_sub.call_args.kwargs["subscription_matches"] == ["testA", "testB"]
        assert Logger._LOGGER_LEVEL == LoggerLevels.VERBOSE


def test_no_config_works(mock_sys_exit):
    with mock_sys_exit(expected_exit_code=0), patch.object(
        sys,
        "argv",
        ["ytdl-sub", "sub", "--log-level", "verbose"],
    ), patch("ytdl_sub.cli.entrypoint._download_subscriptions_from_yaml_files") as mock_sub:
        main()

        assert mock_sub.call_count == 1
        assert mock_sub.call_args.kwargs["subscription_paths"] == ["subscriptions.yaml"]
        assert mock_sub.call_args.kwargs["config"]._name == "default_config"
        assert Logger._LOGGER_LEVEL == LoggerLevels.VERBOSE


def test_uses_default_config_if_present(mock_sys_exit):
    # If a config exists in the ytdl-sub root dir, just use that and do not delete it
    preexisting_default_config = os.path.isfile(DEFAULT_CONFIG_FILE_NAME)
    if not preexisting_default_config:
        open(DEFAULT_CONFIG_FILE_NAME, "a").close()

    try:
        with mock_sys_exit(expected_exit_code=0), patch.object(
            sys,
            "argv",
            ["ytdl-sub", "sub", "--log-level", "verbose"],
        ), patch(
            "ytdl_sub.cli.entrypoint._download_subscriptions_from_yaml_files"
        ) as mock_sub, patch.object(
            ConfigFile, "from_file_path", new=lambda _: ConfigFile(name="test default", value={})
        ):
            main()

            assert mock_sub.call_count == 1
            assert mock_sub.call_args.kwargs["subscription_paths"] == ["subscriptions.yaml"]
            assert mock_sub.call_args.kwargs["config"]._name == "test default"
            assert Logger._LOGGER_LEVEL == LoggerLevels.VERBOSE
    finally:
        if not preexisting_default_config:
            FileHandler.delete(DEFAULT_CONFIG_FILE_NAME)


def test_no_positional_arg_command(mock_sys_exit, tv_show_config_path):
    with mock_sys_exit(expected_exit_code=1), patch.object(
        sys,
        "argv",
        ["ytdl-sub", "-c", tv_show_config_path, "--log-level", "verbose"],
    ), patch.object(logging.Logger, "error") as mock_error:
        main()

        assert mock_error.call_count == 1
        assert mock_error.call_args.args[0] == "Must provide one of the commands: sub, dl, view"


def test_bad_config_path(mock_sys_exit):
    with mock_sys_exit(expected_exit_code=1), patch.object(
        sys,
        "argv",
        ["ytdl-sub", "-c", "does_not_exist.yaml", "sub", "--log-level", "verbose"],
    ), patch.object(logging.Logger, "error") as mock_error:
        main()

        assert mock_error.call_count == 1
        assert mock_error.call_args.args[0] == (
            "The config file 'does_not_exist.yaml' could not be found. "
            "Did you set --config correctly?"
        )
