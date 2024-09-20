import os.path
import time

import pytest

from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.logger import LoggerLevels


class TestLogger:
    @pytest.mark.parametrize(
        "log_level",
        [
            LoggerLevels.QUIET,
            LoggerLevels.INFO,
            LoggerLevels.VERBOSE,
            LoggerLevels.DEBUG,
        ],
    )
    def test_logger_level_set(self, log_level):
        Logger.set_log_level(log_level_name=log_level.name)
        assert Logger._LOGGER_LEVEL == log_level

    def test_logger_level_invalid_name(self):
        with pytest.raises(ValueError):
            Logger.set_log_level("nope")

    @pytest.mark.parametrize(
        "log_level",
        [
            LoggerLevels.QUIET,
            LoggerLevels.INFO,
            LoggerLevels.VERBOSE,
            LoggerLevels.DEBUG,
        ],
    )
    def test_logger_warning_stdout(self, capsys, log_level):
        Logger._LOGGER_LEVEL = log_level
        logger = Logger.get(name="name_test")

        logger.warning("test")
        captured = capsys.readouterr()

        # Warning should always be captured
        assert captured.out == "[ytdl-sub:name_test] test\n"

    @pytest.mark.parametrize(
        "log_level, outputs_to_stdout",
        [
            (LoggerLevels.QUIET, False),
            (LoggerLevels.INFO, True),
            (LoggerLevels.VERBOSE, True),
            (LoggerLevels.DEBUG, True),
        ],
    )
    def test_logger_info_stdout(self, capsys, log_level, outputs_to_stdout):
        Logger._LOGGER_LEVEL = log_level
        logger = Logger.get(name="name_test")

        logger.info("test")
        captured = capsys.readouterr()

        if outputs_to_stdout:
            assert captured.out == "[ytdl-sub:name_test] test\n"
        else:
            assert not captured.out

    @pytest.mark.parametrize(
        "log_level, outputs_to_stdout",
        [
            (LoggerLevels.QUIET, False),
            (LoggerLevels.INFO, False),
            (LoggerLevels.VERBOSE, False),
            (LoggerLevels.DEBUG, True),
        ],
    )
    def test_logger_debug_stdout(self, capsys, log_level, outputs_to_stdout):
        Logger._LOGGER_LEVEL = log_level
        logger = Logger.get(name="name_test")

        logger.debug("test")
        captured = capsys.readouterr()

        if outputs_to_stdout:
            assert captured.out == "[ytdl-sub:name_test] test\n"
        else:
            assert not captured.out

    @pytest.mark.parametrize(
        "log_level",
        [
            LoggerLevels.QUIET,
            LoggerLevels.INFO,
            LoggerLevels.VERBOSE,
            LoggerLevels.DEBUG,
        ],
    )
    def test_logger_always_outputs_to_debug_file(self, log_level):
        Logger._LOGGER_LEVEL = log_level
        logger = Logger.get(name="name_test")

        logger.info("info test")
        logger.debug("debug test")

        with open(Logger._DEBUG_LOGGER_FILE.name, "r", encoding="utf-8") as log_file:
            lines = log_file.readlines()

        assert lines == ["[ytdl-sub:name_test] info test\n", "[ytdl-sub:name_test] debug test\n"]

        # Ensure the file cleans up too
        Logger.cleanup()
        assert not os.path.isfile(Logger._DEBUG_LOGGER_FILE.name)

    @pytest.mark.parametrize("has_error", [True, False])
    def test_logger_can_be_cleaned_during_execution(self, has_error: bool):
        Logger._LOGGER_LEVEL = LoggerLevels.INFO
        logger = Logger.get(name="name_test")

        for iteration in range(2):
            logger.info("info test")
            logger.debug("debug test")

            with open(Logger._DEBUG_LOGGER_FILE.name, "r", encoding="utf-8") as log_file:
                lines = log_file.readlines()

            assert lines == [
                "[ytdl-sub:name_test] info test\n",
                "[ytdl-sub:name_test] debug test\n",
            ]

            try:
                raise ValueError("some error")
            except ValueError as exc:
                Logger.log_exception(exception=exc)

            time.sleep(0.1)  # flush time
            Logger.cleanup(has_error=has_error)
            assert not os.path.isfile(Logger.debug_log_filename())

            assert not has_error == (not os.path.isfile(Logger.error_log_filename()))
            if has_error:
                with open(Logger.error_log_filename(), mode="r", encoding="utf-8") as err_file:
                    err_logs = err_file.readlines()
                    expected = [
                        "[ytdl-sub:name_test] info test\n",
                        "[ytdl-sub:name_test] debug test\n",
                        "[ytdl-sub] An uncaught error occurred:\n",
                        "Traceback (most recent call last):\n",
                        '  File "/home/j/workspace/ytdl-sub/tests/unit/utils/test_logger.py", line 132, in test_logger_can_be_cleaned_during_execution\n',
                        '    raise ValueError("some error")\n',
                        "ValueError: some error\n",
                        "[ytdl-sub] Version 2023.03.24+14e4a4b\n",
                        f"Please upload the error log file '{Logger.error_log_filename()}' and make a Github issue at https://github.com/jmbannon/ytdl-sub/issues with your config and command/subscription yaml file to reproduce. Thanks for trying ytdl-sub!\n",
                    ]

                    assert err_logs[0:4] == expected[0:4]
                    assert err_logs[8] == expected[8]

                    if iteration == 1:
                        err_lines = len(expected)

                        # Two errors occurred, error log should contain 2
                        assert err_logs[err_lines : err_lines + 4] == expected[0:4]
                        assert err_logs[err_lines + 8] == expected[8]

    @pytest.mark.parametrize(
        "log_level, expected_stdout",
        [
            (LoggerLevels.QUIET, False),
            (LoggerLevels.INFO, False),
            (LoggerLevels.VERBOSE, True),
            (LoggerLevels.DEBUG, True),
        ],
    )
    def test_handle_external_logs(self, capsys, log_level, expected_stdout):
        Logger._LOGGER_LEVEL = log_level
        expected_lines = [
            "[ytdl-sub:name_test] test line 1\n",
            "[ytdl-sub:name_test] test line 2\n",
        ]
        with Logger.handle_external_logs(name="name_test"):
            print("test line 1")
            print("test line 2")

        # Wait for flushed logs
        time.sleep(0.1)

        # Ensure it goes to stdout only if it is expected to
        captured = capsys.readouterr()
        if expected_stdout:
            assert captured.out == "".join(expected_lines)
        else:
            assert not captured.out

        # Ensure it always go to the debug file
        with open(Logger._DEBUG_LOGGER_FILE.name, "r", encoding="utf-8") as log_file:
            lines = log_file.readlines()
        assert lines == expected_lines
