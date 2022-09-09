import os
import time

import pytest

from ytdl_sub.cli.main import _working_directory_lock
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.utils.exceptions import ValidationException


@pytest.fixture
def config() -> ConfigFile:
    return ConfigFile(
        name="config", value={"configuration": {"working_directory": "test"}, "presets": {}}
    )


def test_working_directory_lock(config: ConfigFile):
    new_pid = os.fork()
    if new_pid == 0:  # is child
        with _working_directory_lock(config=config):
            time.sleep(3)
        return

    time.sleep(1)
    with pytest.raises(ValidationException, match="Cannot run two instances of ytdl-sub"):
        with _working_directory_lock(config=config):
            time.sleep(1)

    time.sleep(3)
    with _working_directory_lock(config=config):
        pass
