import os.path

import pytest

from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.logger import LoggerLevels


@pytest.fixture(autouse=True)
def cleanup_debug_file():
    Logger.set_log_level(log_level_name=LoggerLevels.DEBUG.name)
    yield
    Logger.cleanup()


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
        for handler in logger.handlers:
            handler.close()

        Logger.cleanup()
        assert not os.path.isfile(Logger._DEBUG_LOGGER_FILE.name)

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
