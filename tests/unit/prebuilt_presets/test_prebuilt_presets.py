from typing import Dict
from typing import List

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.prebuilt_presets.tv_show import PrebuiltJellyfinTVShowPresets
from ytdl_sub.prebuilt_presets.tv_show import PrebuiltKodiTVShowPresets
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def config(working_directory) -> ConfigFile:
    return ConfigFile(
        name="config",
        value={"configuration": {"working_directory": working_directory}, "presets": {}},
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
            "season_by_year_month__episode_by_day",
            "season_by_year__episode_by_month_day",
            "season_by_year__episode_by_month_day_reversed",
        ],
    )
    @pytest.mark.parametrize(
        "episode_hour_granularity_preset",
        [
            None,
            "episode_add_hour_granularity",
            "episode_add_hour_granularity_reversed",
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
            preset_name=f"{media_player_preset}_test",
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
            "season_by_collection__episode_by_year_month_day",
            "season_by_collection__episode_by_year_month_day_reversed",
        ],
    )
    @pytest.mark.parametrize(
        "episode_hour_granularity_preset",
        [
            None,
            "episode_add_hour_granularity",
            "episode_add_hour_granularity_reversed",
        ],
    )
    @pytest.mark.parametrize("season_indices", [[1], [1, 2]])
    @pytest.mark.parametrize("is_season_1_youtube_channel", [True, False])
    def test_collection_presets_compile(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
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
            parent_presets.append(f"tv_show_collection_season_{season_index}")
            if season_index == 1 and is_season_1_youtube_channel:
                parent_presets[-1] += "_youtube_channel"

            overrides = dict(
                overrides,
                **{
                    f"collection_season_{season_index}_name": f"Season {season_index}",
                    f"collection_season_{season_index}_url": f"https://season.{season_index}.com",
                },
            )

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict={
                "preset": parent_presets,
                "overrides": dict(
                    overrides,
                    **{
                        "tv_show_name": "Test TV Show",
                        "tv_show_directory": output_directory,
                    },
                ),
            },
        )

        output_transactoin = subscription.download(dry_run=False)
        assert output_transactoin
