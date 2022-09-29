from typing import Dict
from typing import List

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.prebuilt_presets import PrebuiltKodiTVShowPresets
from ytdl_sub.prebuilt_presets.tv_show.out import PrebuiltJellyfinTVShowPresets


@pytest.fixture
def config() -> ConfigFile:
    return ConfigFile(
        name="config", value={"configuration": {"working_directory": "test"}, "presets": {}}
    )


class TestPrebuiltTVShowPresets:
    @pytest.mark.parametrize(
        "preset_name",
        [
            *PrebuiltKodiTVShowPresets.get_non_collection_preset_names(),
            *PrebuiltJellyfinTVShowPresets.get_non_collection_preset_names(),
        ],
    )
    def test_non_collection_presets_compile(self, config, preset_name: str):
        preset = Preset.from_dict(
            config=config,
            preset_name=f"{preset_name}-test",
            preset_dict={
                "preset": preset_name,
                "overrides": {
                    "url": "https://your.name.here",
                    "tv_show_name": "test tv show",
                    "tv_show_directory": "output_path",
                },
            },
        )
        assert preset

    @pytest.mark.parametrize(
        "preset_name",
        [
            *PrebuiltKodiTVShowPresets.get_collection_preset_names(),
            *PrebuiltJellyfinTVShowPresets.get_collection_preset_names(),
        ],
    )
    @pytest.mark.parametrize(
        "season_indices", [[1], [1, 2], [1, 2, 3], [1, 2, 3, 4], [1, 2, 3, 4, 5], [4, 1]]
    )
    @pytest.mark.parametrize("is_season_1_youtube_channel", [True, False])
    def test_collection_presets_compile(
        self, config, preset_name: str, season_indices: List[int], is_season_1_youtube_channel: bool
    ):
        parent_presets: List[str] = [preset_name]
        overrides: Dict[str, str] = {}
        for season_index in season_indices:
            parent_presets.append(f"tv-show-collection-season-{season_index}")
            if season_index == 1 and is_season_1_youtube_channel:
                parent_presets[-1] += "-youtube-channel"

            overrides = dict(
                overrides,
                **{
                    f"collection_season_{season_index}_name": f"Season {season_index}",
                    f"collection_season_{season_index}_url": f"https://season.{season_index}.com",
                },
            )

        preset = Preset.from_dict(
            config=config,
            preset_name=f"{preset_name}-test",
            preset_dict={
                "preset": parent_presets,
                "overrides": dict(
                    overrides,
                    **{
                        "tv_show_name": "test tv show",
                        "tv_show_directory": "output_path",
                    },
                ),
            },
        )
        assert preset
