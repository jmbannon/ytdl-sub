from typing import Dict

import pytest

from ytdl_sub.config.config_file import ConfigFile


@pytest.fixture
def config_file() -> ConfigFile:
    return ConfigFile(
        name="config",
        value={
            "configuration": {"working_directory": "."},
            "presets": {
                "parent_preset_0": {
                    "nfo_tags": {"tags": {"key-1": "preset_0"}},
                    "overrides": {"current_override": "parent_preset_0"},
                },
                "parent_preset_1": {
                    "preset": "parent_preset_0",
                    "nfo_tags": {
                        "nfo_name": "{uid}.nfo",
                        "nfo_root": "root",
                        "tags": {"key-2": "preset_1"},
                    },
                    "overrides": {"current_override": "parent_preset_1"},
                },
                "parent_preset_2": {
                    "nfo_tags": {
                        "nfo_name": "{uid}.nfo",
                        "nfo_root": "root",
                        "tags": {"key-2": "preset_2", "key-3": "preset_2"},
                    },
                    "overrides": {"current_override": "parent_preset_2"},
                },
                "parent_preset_3": {
                    "preset": ["parent_preset_1", "parent_preset_2"],
                    "overrides": {"current_override": "parent_preset_3"},
                },
                "preset_self_loop": {"preset": "preset_self_loop"},
                "preset_loop_0": {"preset": "preset_loop_1"},
                "preset_loop_1": {"preset": "preset_loop_0"},
            },
        },
    )


@pytest.fixture
def output_options() -> Dict:
    return {
        "output_directory": "some dir",
        "file_name": "{uid}",
    }


@pytest.fixture
def youtube_video() -> Dict:
    return {
        "url": "youtube.com/watch?v=123abc",
    }
