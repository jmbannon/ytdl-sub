import pytest

from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.logger import LoggerLevels


@pytest.fixture(autouse=True)
def cleanup_debug_file():
    yield

    Logger.cleanup(delete_debug_file=True)


class TestLogger:
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
        Logger.LEVEL = log_level
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
        Logger.LEVEL = log_level
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
    def test_logger_always_outputs_to_debug_file(self, capsys, log_level):
        Logger.LEVEL = log_level
        logger = Logger.get(name="name_test")

        logger.info("info test")
        logger.debug("debug test")

        with open(Logger._DEBUG_LOGGER_FILE.name, "r", encoding="utf-8") as log_file:
            lines = log_file.readlines()

        assert lines == ["[ytdl-sub:name_test] info test\n", "[ytdl-sub:name_test] debug test\n"]
