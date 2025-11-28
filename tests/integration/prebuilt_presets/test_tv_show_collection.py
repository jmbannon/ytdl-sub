import re
from typing import Dict
from typing import List

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.prebuilt_presets.tv_show import TvShowCollectionPresets
from ytdl_sub.script.utils.exceptions import UserThrownRuntimeError
from ytdl_sub.subscriptions.subscription import Subscription

DEFAULT_EPISODE_ORDERING = "upload-year-month-day"


class TestPrebuiltTvShowCollectionPresets:

    @staticmethod
    def run(
        config: ConfigFile,
        subscription_name: str,
        output_directory: str,
        media_player_preset: str,
        episode_ordering: str,
        season_indices: List[int],
        is_youtube_channel: bool = True,
    ):
        expected_summary_name = "integration/collection/{}/{}/s_{}/is_yt_{}".format(
            media_player_preset.split(" ")[0],
            episode_ordering,
            len(season_indices),
            int(is_youtube_channel),
        )

        overrides: Dict[str, str] = {}
        for season_index in season_indices:
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
                "preset": media_player_preset,
                "overrides": dict(
                    overrides,
                    **{
                        "tv_show_name": "Best Prebuilt TV Show Collection",
                        "tv_show_directory": output_directory,
                        "tv_show_collection_episode_ordering": episode_ordering,
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
        reformatted_tv_show_collection_episode_ordering = "playlist-index-reversed"
        reformatted_expected_summary_name = "integration/collection/{}/{}/s_{}/is_yt_{}".format(
            media_player_preset.split(" ")[0],
            reformatted_tv_show_collection_episode_ordering,
            len(season_indices),
            int(is_youtube_channel),
        )

        reformatted_subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict={
                "preset": media_player_preset,
                "output_options": {
                    "migrated_download_archive_name": ".ytdl-sub-{tv_show_name_sanitized}-download-archive.json"
                },
                "overrides": dict(
                    overrides,
                    **{
                        "tv_show_name": "Best Prebuilt TV Show Collection",
                        "tv_show_directory": output_directory,
                        "tv_show_collection_episode_ordering": reformatted_tv_show_collection_episode_ordering,
                    },
                ),
            },
        )

        reformatted_transaction_log = reformatted_subscription.update_with_info_json(dry_run=False)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=reformatted_transaction_log,
            transaction_log_summary_file_name=(
                f"{expected_summary_name}_reformatted_to_{reformatted_tv_show_collection_episode_ordering}.txt"
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
                episode_ordering=DEFAULT_EPISODE_ORDERING,
                season_indices=season_indices,
            )

    @pytest.mark.parametrize(
        "episode_ordering",
        [
            "upload-year-month-day",
            "upload-year-month-day-reversed",
            "release-year-month-day",
            "release-year-month-day-reversed",
            "playlist-index",
            "playlist-index-reversed",
        ],
    )
    @pytest.mark.parametrize("season_indices", [[1], [1, 2]])
    def test_episode_ordering_presets(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        episode_ordering: str,
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
                episode_ordering=episode_ordering,
                season_indices=season_indices,
            )

    def test_invalid_episode_ordering(
        self, config, subscription_name, output_directory, mock_download_collection_entries
    ):
        expected_message = (
            "tv_show_collection_episode_ordering must be one of the following: "
            '"upload-year-month-day", '
            '"upload-year-month-day-reversed", '
            '"release-year-month-day", '
            '"release-year-month-day-reversed", '
            '"playlist-index", '
            '"playlist-index-reversed"'
        )

        with (
            mock_download_collection_entries(is_youtube_channel=True, num_urls=1),
            pytest.raises(UserThrownRuntimeError, match=re.escape(expected_message)),
        ):
            self.run(
                config=config,
                subscription_name=subscription_name,
                output_directory=output_directory,
                media_player_preset="Kodi TV Show Collection",
                episode_ordering="does-not-exist",
                season_indices=[1],
            )
