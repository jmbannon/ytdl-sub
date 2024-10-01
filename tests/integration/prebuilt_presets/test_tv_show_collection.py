from typing import Dict
from typing import List

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.prebuilt_presets.tv_show import TvShowCollectionEpisodeFormattingPresets
from ytdl_sub.prebuilt_presets.tv_show import TvShowCollectionPresets
from ytdl_sub.subscriptions.subscription import Subscription

DEPRECATED_TV_SHOW_PRESET_EQUIVALENTS = {
    "Kodi TV Show Collection": "kodi_tv_show_collection",
    "Jellyfin TV Show Collection": "jellyfin_tv_show_collection",
    "Plex TV Show Collection": "plex_tv_show_collection",
}

DEFAULT_EPISODE_ORDERING_PRESET = "season_by_collection__episode_by_year_month_day"


class TestPrebuiltTvShowCollectionPresets:

    @staticmethod
    def run(
        config: ConfigFile,
        subscription_name: str,
        output_directory: str,
        media_player_preset: str,
        tv_show_structure_preset: str,
        season_indices: List[int],
        is_youtube_channel: bool = True,
    ):
        expected_summary_name = "unit/{}/{}/s_{}/is_yt_{}".format(
            DEPRECATED_TV_SHOW_PRESET_EQUIVALENTS[media_player_preset],
            tv_show_structure_preset,
            len(season_indices),
            int(is_youtube_channel),
        )
        parent_presets: List[str] = [media_player_preset, tv_show_structure_preset]

        overrides: Dict[str, str] = {}
        for season_index in season_indices:
            parent_presets.append(f"collection_season_{season_index}")

            overrides = dict(
                overrides,
                **{
                    f"s0{season_index}_name": f"Named Season {season_index}",
                    f"s0{season_index}_url": f"https://season.{season_index}.com",
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
                        "tv_show_name": "Best Prebuilt TV Show Collection",
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
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name=f"{expected_summary_name}.json",
        )

        ###################################### Perform reformat
        reformatted_tv_show_structure_preset = (
            "season_by_collection__episode_by_playlist_index_reversed"
        )
        reformatted_expected_summary_name = "unit/{}/{}/s_{}/is_yt_{}".format(
            DEPRECATED_TV_SHOW_PRESET_EQUIVALENTS[media_player_preset],
            reformatted_tv_show_structure_preset,
            len(season_indices),
            int(is_youtube_channel),
        )

        reformatted_subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict={
                "preset": parent_presets + [reformatted_tv_show_structure_preset],
                "output_options": {
                    "migrated_download_archive_name": ".ytdl-sub-{tv_show_name_sanitized}-download-archive.json"
                },
                "overrides": dict(
                    overrides,
                    **{
                        "tv_show_name": "Best Prebuilt TV Show Collection",
                        "tv_show_directory": output_directory,
                    },
                ),
            },
        )

        reformatted_transaction_log = reformatted_subscription.update_with_info_json(dry_run=False)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=reformatted_transaction_log,
            transaction_log_summary_file_name=(
                f"{expected_summary_name}_reformatted_to_{reformatted_tv_show_structure_preset}.txt"
            ),
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name=f"{reformatted_expected_summary_name}_migrated.json",
        )

    @pytest.mark.parametrize("media_player_preset", TvShowCollectionPresets.preset_names)
    @pytest.mark.parametrize("season_indices", [[1], [1, 2]])
    def test_tv_show_collection_presets(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        media_player_preset: str,
        season_indices: List[int],
    ):

        with mock_download_collection_entries(
            is_youtube_channel=True, num_urls=len(season_indices)
        ):
            self.run(
                config=config,
                subscription_name=subscription_name,
                output_directory=output_directory,
                media_player_preset=media_player_preset,
                tv_show_structure_preset=DEFAULT_EPISODE_ORDERING_PRESET,
                season_indices=season_indices,
            )

    @pytest.mark.parametrize(
        "episode_ordering_preset", TvShowCollectionEpisodeFormattingPresets.preset_names
    )
    @pytest.mark.parametrize("season_indices", [[1], [1, 2]])
    def test_episode_ordering_presets(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        episode_ordering_preset: str,
        season_indices: List[int],
    ):

        with mock_download_collection_entries(
            is_youtube_channel=True, num_urls=len(season_indices)
        ):
            self.run(
                config=config,
                subscription_name=subscription_name,
                output_directory=output_directory,
                media_player_preset="Kodi TV Show Collection",
                tv_show_structure_preset=episode_ordering_preset,
                season_indices=season_indices,
            )
