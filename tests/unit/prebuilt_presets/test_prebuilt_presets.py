from typing import List

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.prebuilt_presets import PrebuiltKodiTVShowPresets

@pytest.fixture
def config() -> ConfigFile:
    return ConfigFile(
        name="config", value={"configuration": {"working_directory": "test"}, "presets": {}}
    )

class TestPrebuiltTVShowPresets:



    @pytest.mark.parametrize("preset_name", PrebuiltKodiTVShowPresets.get_preset_names())
    def test_presets_compile(self, config, preset_name: str):
        Preset.from_dict(
            config=config,
            preset_name=f"{preset_name}-test",
            preset_dict={
                'preset': preset_name,
                'overrides': {
                    'tv_show_name': 'test tv show',
                    'tv_show_directory': 'output_path'
                }
            }
        )