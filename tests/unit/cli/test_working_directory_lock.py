import os
import time

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.file_lock import working_directory_lock
from ytdl_sub.utils.system import IS_WINDOWS


def test_working_directory_lock(default_config: ConfigFile):
    if IS_WINDOWS:
        return

    new_pid = os.fork()
    if new_pid == 0:  # is child
        with working_directory_lock(config=default_config):
            time.sleep(3)
        return

    time.sleep(1)
    with pytest.raises(ValidationException, match="Cannot run two instances of ytdl-sub"):
        with working_directory_lock(config=default_config):
            time.sleep(1)

    time.sleep(3)
    with working_directory_lock(config=default_config):
        pass
