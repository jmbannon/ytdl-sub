import logging
import sys
from typing import Optional


class Logger:
    @classmethod
    def _get_formatter(cls) -> logging.Formatter:
        """
        Returns
        -------
        Formatter for all ytdl-sub loggers
        """
        return logging.Formatter("[%(name)s] %(message)s")

    @classmethod
    def _get_handler(cls) -> logging.StreamHandler:
        """
        Returns
        -------
        Logger handler
        """
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        handler.setFormatter(cls._get_formatter())
        return handler

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
        logger_name = "ytdl-sub"
        if name:
            logger_name += f":{name}"

        logger = logging.Logger(name=logger_name)
        logger.addHandler(cls._get_handler())
        return logger
