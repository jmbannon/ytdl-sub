from typing import Dict
from typing import List

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.prebuilt_presets.tv_show import PrebuiltJellyfinTVShowPresets
from ytdl_sub.prebuilt_presets.tv_show import PrebuiltKodiTVShowPresets


@pytest.fixture
def config() -> ConfigFile:
    return ConfigFile(
        name="config", value={"configuration": {"working_directory": "test"}, "presets": {}}
    )


class TestPrebuiltTVShowPresets:
    @pytest.mark.parametrize(
        "media_player_preset",
        [
            *PrebuiltKodiTVShowPresets.get_non_collection_preset_names(),
            *PrebuiltJellyfinTVShowPresets.get_non_collection_preset_names(),
        ],
    )
    @pytest.mark.parametrize(
        "tv_show_structure_preset",
        [
            "season-by-year-month--episode-by-day",
            "season-by-year--episode-by-month-day",
            "season-by-year--episode-by-month-day-reversed",
        ],
    )
    @pytest.mark.parametrize(
        "episode_hour_granularity_preset",
        [
            None,
            "episode-add-hour-granularity",
            "episode-add-hour-granularity-reversed",
        ],
    )
    def test_non_collection_presets_compile(
        self,
        config: ConfigFile,
        media_player_preset: str,
        tv_show_structure_preset: str,
        episode_hour_granularity_preset: str,
    ):
        parent_presets = [media_player_preset, tv_show_structure_preset]
        if episode_hour_granularity_preset:
            parent_presets.append(episode_hour_granularity_preset)

        preset = Preset.from_dict(
            config=config,
            preset_name=f"{media_player_preset}-test",
            preset_dict={
                "preset": parent_presets,
                "overrides": {
                    "url": "https://your.name.here",
                    "tv_show_name": "test tv show",
                    "tv_show_directory": "output_path",
                },
            },
        )
        assert preset

    @pytest.mark.parametrize(
        "media_player_preset",
        [
            *PrebuiltKodiTVShowPresets.get_collection_preset_names(),
            *PrebuiltJellyfinTVShowPresets.get_collection_preset_names(),
        ],
    )
    @pytest.mark.parametrize(
        "tv_show_structure_preset",
        [
            "season-by-collection--episode-by-year-month-day",
            "season-by-collection--episode-by-year-month-day-reversed",
        ],
    )
    @pytest.mark.parametrize(
        "episode_hour_granularity_preset",
        [
            None,
            "episode-add-hour-granularity",
            "episode-add-hour-granularity-reversed",
        ],
    )
    @pytest.mark.parametrize("season_indices", [[1], [1, 2, 3, 4, 5]])
    @pytest.mark.parametrize("is_season_1_youtube_channel", [True, False])
    def test_collection_presets_compile(
        self,
        config,
        media_player_preset: str,
        tv_show_structure_preset: str,
        episode_hour_granularity_preset: str,
        season_indices: List[int],
        is_season_1_youtube_channel: bool,
    ):
        parent_presets: List[str] = [media_player_preset, tv_show_structure_preset]
        if episode_hour_granularity_preset:
            parent_presets.append(episode_hour_granularity_preset)

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
            preset_name=f"{media_player_preset}-test",
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
