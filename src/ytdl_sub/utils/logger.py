import contextlib
import io
import logging
import os
import sys
import tempfile
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


class Logger:

    # The level set via CLI arguments
    LEVEL = LoggerLevels.DEBUG

    _DEBUG_LOGGER_FILE = None

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
        handler.setLevel(LoggerLevels.to_logging_level(cls.LEVEL))
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
        if stdout and cls.LEVEL >= LoggerLevels.INFO:
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
        redirect_stream = io.StringIO()
        redirect_handler = logging.StreamHandler(redirect_stream)
        redirect_handler.setLevel(LoggerLevels.to_logging_level(cls.LEVEL))
        redirect_handler.setFormatter(cls._get_formatter())

        write_to_stdout = cls.LEVEL >= LoggerLevels.VERBOSE
        write_to_debug_file = True

        logger = cls._get(name=name, stdout=write_to_stdout, debug_file=write_to_debug_file)
        logger.addHandler(redirect_handler)

        with contextlib.redirect_stdout(new_target=redirect_stream):
            with contextlib.redirect_stderr(new_target=redirect_stream):
                yield

        redirect_stream.flush()

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
