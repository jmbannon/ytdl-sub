import tempfile

import pytest

from ytdl_sub.config.config_file import ConfigFile


@pytest.fixture()
def output_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture()
def music_video_config():
    return ConfigFile.from_file_path(config_path="examples/kodi_music_videos_config.yaml")


@pytest.fixture()
def channel_as_tv_show_config():
    return ConfigFile.from_file_path(config_path="examples/kodi_tv_shows_config.yaml")


@pytest.fixture
def soundcloud_discography_config():
    return ConfigFile.from_file_path(config_path="examples/soundcloud_discography_config.yaml")
