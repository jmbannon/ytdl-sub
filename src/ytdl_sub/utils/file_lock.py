import errno
import os
import sys
from contextlib import contextmanager
from pathlib import Path

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.logger import Logger

logger = Logger.get()


@contextmanager
def _working_directory_lock_unix(config: ConfigFile):
    """
    Create and try to lock the file /tmp/working_directory_name

    Raises
    ------
    ValidationException
        Lock is acquired from another process running ytdl-sub in the same working directory
    OSError
        Other lock error occurred
    """
    # pylint: disable=import-outside-toplevel
    import fcntl

    working_directory_path = Path(os.getcwd()) / config.config_options.working_directory
    lock_file_path = (
        Path(os.getcwd())
        / config.config_options.lock_directory
        / str(working_directory_path).replace("/", "_")
    )

    lock_file = open(lock_file_path, "w", encoding="utf-8")

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


@contextmanager
def working_directory_lock(config: ConfigFile):
    if sys.platform.startswith("win32"):
        logger.info(
            "Working directory lock not supported in Windows. "
            "Ensure only one instance of ytdl-sub runs at once using working directory %s",
            config.config_options.working_directory,
        )
        yield
    else:
        with _working_directory_lock_unix(config):
            yield
