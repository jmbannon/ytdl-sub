import errno
import os
from contextlib import contextmanager
from pathlib import Path

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.system import IS_WINDOWS

logger = Logger.get()

if IS_WINDOWS:

    @contextmanager
    def working_directory_lock(config: ConfigFile):
        """Windows does not support working directory lock"""
        logger.info(
            "Working directory lock not supported in Windows. "
            "Ensure only one instance of ytdl-sub runs at once using working directory %s",
            config.config_options.working_directory,
        )
        yield

else:
    import fcntl

    @contextmanager
    def working_directory_lock(config: ConfigFile):
        """
        Create and try to lock the file /tmp/working_directory_name

        Raises
        ------
        ValidationException
            Lock is acquired from another process running ytdl-sub in the same working directory
        OSError
            Other lock error occurred
        """
        working_directory_path = Path(os.getcwd()) / config.config_options.working_directory
        lock_file_path = (
            Path(os.getcwd())
            / config.config_options.lock_directory
            / str(working_directory_path).replace("/", "_")
        )

        try:
            lock_file = open(lock_file_path, "w", encoding="utf-8")
        except FileNotFoundError as exc:
            # pylint: disable=line-too-long
            raise ValidationException(
                "Failed to create a file-lock to prevent multiple instances of ytdl-sub from "
                "colliding with each other. If you get this error, it typically means it tried to "
                "create the file in a directory that is not a part of the same filesystem that "
                "ytdl-sub is running on. See "
                "https://ytdl-sub.readthedocs.io/en/latest/config_reference/config_yaml.html "
                "on how to change the directory that this lock gets written to."
            ) from exc
            # pylint: enable=line-too-long

        try:
            fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if exc.errno in (errno.EACCES, errno.EAGAIN):
                raise ValidationException(
                    "Cannot run two instances of ytdl-sub "
                    "with the same working directory at the same time"
                ) from exc
            lock_file.close()
            raise exc

        try:
            yield
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
            lock_file.close()
