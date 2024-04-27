import contextlib
import io
import logging
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Optional

from ytdl_sub import __local_version__
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.file_handler import FileHandler


@dataclass
class LoggerLevel:
    name: str
    level: int
    logging_level: int


class LoggerLevels:
    """
    Custom log levels
    """

    QUIET = LoggerLevel(name="quiet", level=0, logging_level=logging.WARNING)  # Only warnings
    INFO = LoggerLevel(name="info", level=10, logging_level=logging.INFO)  # ytdl-sub info logs
    VERBOSE = LoggerLevel(name="verbose", level=20, logging_level=logging.INFO)  # ytdl-sub + yt-dlp
    DEBUG = LoggerLevel(
        name="debug", level=30, logging_level=logging.DEBUG
    )  # ytdl-sub + yt-dlp debug logs

    @classmethod
    def all(cls) -> List[LoggerLevel]:
        """
        Returns
        -------
        All log levels
        """
        return [cls.QUIET, cls.INFO, cls.VERBOSE, cls.DEBUG]

    @classmethod
    def from_str(cls, name: str) -> LoggerLevel:
        """
        Parameters
        ----------
        name
            The log level name

        Raises
        ------
        ValueError
            Name is not a valid logger level
        """
        for logger_level in cls.all():
            if name == logger_level.name:
                return logger_level
        raise ValueError("Invalid logger level name")

    @classmethod
    def names(cls) -> List[str]:
        """
        Returns
        -------
        All log level names
        """
        return [logger_level.name for logger_level in cls.all()]


class StreamToLogger(io.StringIO):
    def __init__(self, logger: logging.Logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = logger

    def write(self, __s: str) -> int:
        """
        Writes to the logger and stream
        """
        if __s != "\n":
            self._logger.info(__s.removesuffix("\n"))
        return super().write(__s)


class Logger:

    # The level set via CLI arguments
    _LOGGER_LEVEL: LoggerLevel = LoggerLevels.DEBUG

    # Ignore 'using with' warning since this will be cleaned up later
    # pylint: disable=R1732
    _DEBUG_LOGGER_FILE = tempfile.NamedTemporaryFile(prefix="ytdl-sub.", delete=False)
    _ERROR_LOG_FILE = tempfile.NamedTemporaryFile(prefix="ytdl-sub.errors", delete=False)
    # pylint: enable=R1732

    # Keep track of all Loggers created
    _LOGGERS: List[logging.Logger] = []

    @classmethod
    def debug_log_filename(cls) -> str:
        """
        Returns
        -------
        File name of the debug log file
        """
        return cls._DEBUG_LOGGER_FILE.name

    @classmethod
    def error_log_filename(cls) -> str:
        """
        Returns
        -------
        File name of the error log file
        """
        return cls._ERROR_LOG_FILE.name

    @classmethod
    def set_log_level(cls, log_level_name: str):
        """
        Parameters
        ----------
        log_level_name
            Name of the log level to set
        """
        cls._LOGGER_LEVEL = LoggerLevels.from_str(name=log_level_name)

    @classmethod
    def _get_formatter(cls) -> logging.Formatter:
        """
        Returns
        -------
        Formatter for all ytdl-sub loggers
        """
        return logging.Formatter("[%(name)s] %(message)s")

    @classmethod
    def _get_stdout_handler(cls) -> logging.StreamHandler:
        """
        Returns
        -------
        Logger handler
        """
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(cls._LOGGER_LEVEL.logging_level)
        handler.setFormatter(cls._get_formatter())
        return handler

    @classmethod
    def _get_debug_file_handler(cls) -> logging.FileHandler:
        handler = logging.FileHandler(filename=cls.debug_log_filename(), encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(cls._get_formatter())
        return handler

    @classmethod
    def _get(
        cls, name: Optional[str] = None, stdout: bool = True, debug_file: bool = True
    ) -> logging.Logger:
        logger_name = "ytdl-sub"
        if name:
            logger_name += f":{name}"

        logger = logging.Logger(name=logger_name, level=logging.DEBUG)
        if stdout:
            logger.addHandler(cls._get_stdout_handler())
        if debug_file:
            logger.addHandler(cls._get_debug_file_handler())

        cls._LOGGERS.append(logger)
        return logger

    @classmethod
    def get(cls, name: Optional[str] = None) -> logging.Logger:
        """
        Parameters
        ----------
        name
            Optional. Name of the logger which is included in the prefix like [ytdl-sub:<name>].
            If None, the prefix is just [ytdl-sub]

        Returns
        -------
        A configured logger
        """
        return cls._get(name=name, stdout=True, debug_file=True)

    @classmethod
    @contextlib.contextmanager
    def handle_external_logs(cls, name: Optional[str] = None) -> None:
        """
        Suppresses all stdout and stderr logs. Intended to suppress other packages logs.
        Will always write these logs to the debug logger file.

        Parameters
        ----------
        name
            Optional. Name of the logger which is included in the prefix like [ytdl-sub:<name>].
            If None, the prefix is just [ytdl-sub]mak
        """
        logger = cls._get(
            name=name, stdout=cls._LOGGER_LEVEL.level >= LoggerLevels.VERBOSE.level, debug_file=True
        )

        with StreamToLogger(logger=logger) as redirect_stream:
            try:
                with contextlib.redirect_stdout(new_target=redirect_stream):
                    with contextlib.redirect_stderr(new_target=redirect_stream):
                        yield
            finally:
                redirect_stream.flush()

    @classmethod
    def _append_to_error_log(cls):
        # Any time an exception occurs, dump all debug logs into the error log
        with (
            open(cls.debug_log_filename(), mode="r", encoding="utf-8") as debug_logs,
            open(cls.error_log_filename(), mode="a", encoding="utf-8") as error_logs,
        ):
            error_logs.writelines(debug_logs.readlines())

    @classmethod
    def log_exception(cls, exception: Exception, log_filepath: Optional[Path] = None):
        """
        Logs an exception based on the exception type. Will transfer all
        debug logs into the error log file. This allows for subscriptions to only write to the
        error log if an error occurred - successful subscriptions will clean the debug log file
        w/out any write to the error log.

        Parameters
        ----------
        exception
            The exception to log
        log_filepath
            Optional. The filepath to the debug logs
        """
        logger = cls.get()

        # Log validation exceptions as-is
        if isinstance(exception, ValidationException):
            logger.error(str(exception))
        # Log permission errors explicitly
        elif isinstance(exception, PermissionError):
            logger.error(
                "A permission error occurred:\n%s\n"
                "The user running ytdl-sub must have permission to this file/directory.",
                str(exception),
            )
        # For other uncaught errors, log as bug:
        else:
            logger.exception("An uncaught error occurred:")
            logger.error(
                "Version %s\nPlease upload the error log file '%s' and make a Github "
                "issue at https://github.com/jmbannon/ytdl-sub/issues with your config and "
                "command/subscription yaml file to reproduce. Thanks for trying ytdl-sub!",
                __local_version__,
                log_filepath if log_filepath else Logger.error_log_filename(),
            )

        cls._append_to_error_log()

    @classmethod
    def cleanup(cls, has_error: bool = False):
        """
        Cleans up debug log file left behind
        """
        for logger in cls._LOGGERS:
            for handler in logger.handlers:
                handler.close()

        if has_error:
            cls._append_to_error_log()
        else:
            cls._ERROR_LOG_FILE.close()
            FileHandler.delete(cls.error_log_filename())

        cls._DEBUG_LOGGER_FILE.close()
        FileHandler.delete(cls.debug_log_filename())
