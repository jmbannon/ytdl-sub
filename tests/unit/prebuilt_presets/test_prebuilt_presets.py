from typing import Dict
from typing import List

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.prebuilt_presets.tv_show import PrebuiltJellyfinTVShowPresets
from ytdl_sub.prebuilt_presets.tv_show import PrebuiltKodiTVShowPresets
from ytdl_sub.subscriptions.subscription import Subscription


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
            "season_by_year__episode_by_month_day",
            "season_by_year__episode_by_month_day_reversed",
            "season_by_year__episode_by_month_day_hour",
            "season_by_year__episode_by_month_day_hour_reversed",
            "season_by_year_month__episode_by_day",
            "season_by_year_month__episode_by_day_hour",
        ],
    )
    def test_non_collection_presets_compile(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        media_player_preset: str,
        tv_show_structure_preset: str,
    ):
        expected_summary_name = f"unit/{media_player_preset}/{tv_show_structure_preset}"
        parent_presets = [media_player_preset, tv_show_structure_preset]

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict={
                "preset": parent_presets,
                "overrides": {
                    "url": "https://your.name.here",
                    "tv_show_name": "test tv show",
                    "tv_show_directory": output_directory,
                },
            },
        )

        transaction_log = subscription.download(dry_run=False)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"{expected_summary_name}.txt",
            regenerate_transaction_log=True,
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name=f"{expected_summary_name}.json",
            regenerate_expected_download_summary=True,
        )

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
            "season_by_collection__episode_by_year_month_day_hour",
            "season_by_collection__episode_by_year_month_day_hour_reversed",
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
        season_indices: List[int],
        is_season_1_youtube_channel: bool,
    ):
        expected_summary_name = f"unit/{media_player_preset}/{tv_show_structure_preset}"
        parent_presets: List[str] = [media_player_preset, tv_show_structure_preset]

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

        transaction_log = subscription.download(dry_run=False)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name=f"{expected_summary_name}.txt",
            regenerate_transaction_log=True,
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name=f"{expected_summary_name}.json",
            regenerate_expected_download_summary=True,
        )
