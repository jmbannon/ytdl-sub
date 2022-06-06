import contextlib
import io
import logging
import os
import sys
import tempfile
from typing import List
from typing import Optional


class LoggerLevels:
    """
    Custom log levels
    """

    # No logs whatsoever
    QUIET = 0

    # Only ytdl-sub info logs
    INFO = 10

    # ytdl-sub and yt-dlp info logs
    VERBOSE = 20

    # ytdl-sub and yt-dlp info + debug logs
    DEBUG = 30

    @classmethod
    def to_logging_level(cls, logger_level: int) -> int:
        """
        Parameters
        ----------
        logger_level
            LoggingLevels enum

        Returns
        -------
        logging level
        """
        match logger_level:
            case cls.QUIET:
                return logging.NOTSET
            case cls.DEBUG:
                return logging.DEBUG
            case _:
                return logging.INFO

    @classmethod
    def name_of(cls, log_level: int):
        """
        Parameters
        ----------
        log_level
            The log level

        Returns
        -------
        Name of the log levels
        """
        match log_level:
            case cls.QUIET:
                return "quiet"
            case cls.INFO:
                return "info"
            case cls.VERBOSE:
                return "verbose"
            case cls.DEBUG:
                return "debug"
            case _:
                raise ValueError("Invalid log level")

    @classmethod
    def all(cls) -> List[int]:
        """
        Returns
        -------
        All log levels
        """
        return [cls.QUIET, cls.INFO, cls.VERBOSE, cls.DEBUG]

    @classmethod
    def names(cls) -> List[str]:
        """
        Returns
        -------
        All log level names
        """
        return [cls.name_of(log_level=log_level) for log_level in cls.all()]


class Logger:

    # The level set via CLI arguments
    _LEVEL = LoggerLevels.DEBUG

    _DEBUG_LOGGER_FILE = None

    @classmethod
    def set_log_level(cls, log_level: int):
        cls._LEVEL = log_level

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
        handler.setLevel(LoggerLevels.to_logging_level(cls._LEVEL))
        handler.setFormatter(cls._get_formatter())
        return handler

    @classmethod
    def _get_debug_file_handler(cls) -> logging.FileHandler:
        if cls._DEBUG_LOGGER_FILE is None:
            # Ignore 'using with' warning since this must be cleaned up later
            # pylint: disable=R1732
            cls._DEBUG_LOGGER_FILE = tempfile.NamedTemporaryFile(prefix="ytdl-sub.", delete=False)
            # pylint: enable=R1732

        handler = logging.FileHandler(filename=cls._DEBUG_LOGGER_FILE.name, encoding="utf-8")
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
        if stdout and cls._LEVEL >= LoggerLevels.INFO:
            logger.addHandler(cls._get_stdout_handler())
        if debug_file:
            logger.addHandler(cls._get_debug_file_handler())

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
            If None, the prefix is just [ytdl-sub]
        """
        logger = cls._get(name=name, stdout=cls._LEVEL >= LoggerLevels.VERBOSE, debug_file=True)

        with io.StringIO() as redirect_stream:
            with contextlib.redirect_stdout(new_target=redirect_stream):
                with contextlib.redirect_stderr(new_target=redirect_stream):
                    yield

            redirect_stream.flush()
            logger.info(redirect_stream.getvalue())

    @classmethod
    def cleanup(cls, delete_debug_file: bool = True):
        """
        Cleans up any log files left behind.

        Parameters
        ----------
        delete_debug_file
            Whether to delete the debug log file. Defaults to True.
        """
        cls._DEBUG_LOGGER_FILE.close()

        if delete_debug_file and os.path.isfile(cls._DEBUG_LOGGER_FILE.name):
            os.remove(cls._DEBUG_LOGGER_FILE.name)
