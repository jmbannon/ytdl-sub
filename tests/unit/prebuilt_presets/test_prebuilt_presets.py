import copy
from typing import Dict
from typing import List

import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.prebuilt_presets.music import MusicPresets
from ytdl_sub.prebuilt_presets.tv_show import TvShowByDateEpisodeFormattingPresets
from ytdl_sub.prebuilt_presets.tv_show import TvShowByDatePresets
from ytdl_sub.prebuilt_presets.tv_show import TvShowCollectionEpisodeFormattingPresets
from ytdl_sub.prebuilt_presets.tv_show import TvShowCollectionPresets
from ytdl_sub.prebuilt_presets.tv_show import TvShowCollectionSeasonPresets
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.exceptions import ValidationException


@pytest.mark.parametrize("media_player_preset", TvShowByDatePresets.preset_names)
@pytest.mark.parametrize(
    "tv_show_structure_preset", TvShowByDateEpisodeFormattingPresets.preset_names
)
class TestPrebuiltTVShowPresets:
    def test_compilation(
        self,
        config,
        media_player_preset: str,
        tv_show_structure_preset: str,
    ):
        parent_presets: List[str] = [media_player_preset, tv_show_structure_preset]
        _ = Subscription.from_dict(
            config=config,
            preset_name="preset_test",
            preset_dict={
                "preset": parent_presets,
                "overrides": {
                    "url": "https://your.name.here",
                    "tv_show_name": "test-compile",
                    "tv_show_directory": "output_dir",
                },
            },
        )

    def test_compilation_many_urls(
        self,
        config,
        media_player_preset: str,
        tv_show_structure_preset: str,
    ):
        parent_presets: List[str] = [media_player_preset, tv_show_structure_preset]
        _ = Subscription.from_dict(
            config=config,
            preset_name="preset_test",
            preset_dict={
                "preset": parent_presets,
                "download": "https://second.url",
                "overrides": {
                    "url": "https://your.name.here",
                    "tv_show_name": "test-compile",
                    "tv_show_directory": "output_dir",
                },
            },
        )

    def test_compilation_errors_missing_one(
        self,
        config,
        media_player_preset: str,
        tv_show_structure_preset: str,
    ):
        parent_presets: List[str] = [media_player_preset, tv_show_structure_preset]
        for parent_preset in parent_presets:
            parent_presets_missing_one = copy.deepcopy(parent_presets).remove(parent_preset)

            with pytest.raises(ValidationException):
                _ = Subscription.from_dict(
                    config=config,
                    preset_name="preset_test",
                    preset_dict={
                        "preset": parent_presets_missing_one,
                        "overrides": {
                            "url": "https://your.name.here",
                            "tv_show_name": "test-compile",
                            "tv_show_directory": "output_dir",
                        },
                    },
                )

    @pytest.mark.parametrize("is_youtube_channel", [True, False])
    @pytest.mark.parametrize("is_many_urls", [True, False])
    def test_non_collection_presets_compile(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        media_player_preset: str,
        tv_show_structure_preset: str,
        is_youtube_channel: bool,
        is_many_urls: bool,
    ):
        expected_summary_name = "unit/{}/{}/is_yt_{}{}".format(
            media_player_preset,
            tv_show_structure_preset,
            int(is_youtube_channel),
            "_many_urls" if is_many_urls else "",
        )
        parent_presets = [media_player_preset, tv_show_structure_preset]

        preset_dict = {
            "preset": parent_presets,
            "overrides": {
                "url": "https://your.name.here",
                "tv_show_name": "Best Prebuilt TV Show by Date",
                "tv_show_directory": output_directory,
            },
        }
        if is_many_urls:
            preset_dict["overrides"]["url2"] = "https://url.number.2.here"

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=preset_dict,
        )

        with mock_download_collection_entries(
            is_youtube_channel=is_youtube_channel, num_urls=2 if is_many_urls else 1
        ):
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
        reformatted_tv_show_structure_preset = "season_by_year__episode_by_download_index"
        reformatted_expected_summary_name = "unit/{}/{}/is_yt_{}{}".format(
            media_player_preset,
            reformatted_tv_show_structure_preset,
            int(is_youtube_channel),
            "_many_urls" if is_many_urls else "",
        )

        reformatted_subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict={
                "preset": parent_presets + [reformatted_tv_show_structure_preset],
                "output_options": {
                    "migrated_download_archive_name": ".ytdl-sub-{tv_show_name_sanitized}-download-archive.json"
                },
                "overrides": {
                    "url": "https://your.name.here",
                    "tv_show_name": "Best Prebuilt TV Show by Date",
                    "tv_show_directory": output_directory,
                },
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
@pytest.mark.parametrize(
    "tv_show_structure_preset", TvShowCollectionEpisodeFormattingPresets.preset_names
)
class TestPrebuiltTvShowCollectionPresets:
    @pytest.mark.parametrize("season_preset", TvShowCollectionSeasonPresets.preset_names)
    def test_compilation(
        self,
        config,
        media_player_preset: str,
        tv_show_structure_preset: str,
        season_preset: str,
    ):
        parent_presets: List[str] = [media_player_preset, tv_show_structure_preset, season_preset]
        _ = Subscription.from_dict(
            config=config,
            preset_name="preset_test",
            preset_dict={
                "preset": parent_presets,
                "overrides": {
                    "url": "https://your.name.here",
                    "tv_show_name": "test-compile",
                    "tv_show_directory": "output_dir",
                    f"{season_preset}_url": "https://your.name.here",
                    f"{season_preset}_name": "test season name",
                },
            },
        )

    @pytest.mark.parametrize("season_preset", TvShowCollectionSeasonPresets.preset_names)
    def test_compilation_errors_missing_one(
        self,
        config,
        media_player_preset: str,
        tv_show_structure_preset: str,
        season_preset: str,
    ):
        parent_presets: List[str] = [media_player_preset, tv_show_structure_preset, season_preset]
        for parent_preset in parent_presets:
            parent_presets_missing_one = copy.deepcopy(parent_presets).remove(parent_preset)

            with pytest.raises(ValidationException):
                _ = Subscription.from_dict(
                    config=config,
                    preset_name="preset_test",
                    preset_dict={
                        "preset": parent_presets_missing_one,
                        "overrides": {
                            "url": "https://your.name.here",
                            "tv_show_name": "test-compile",
                            "tv_show_directory": "output_dir",
                            f"{season_preset}_url": "https://your.name.here",
                            f"{season_preset}_name": "test season name",
                        },
                    },
                )

    @pytest.mark.parametrize("season_indices", [[1], [1, 2]])
    @pytest.mark.parametrize("is_youtube_channel", [True, False])
    def test_collection_presets_compile(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        media_player_preset: str,
        tv_show_structure_preset: str,
        season_indices: List[int],
        is_youtube_channel: bool,
    ):
        expected_summary_name = "unit/{}/{}/s_{}/is_yt_{}".format(
            media_player_preset,
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
                    f"collection_season_{season_index}_name": f"Named Season {season_index}",
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
                        "tv_show_name": "Best Prebuilt TV Show Collection",
                        "tv_show_directory": output_directory,
                    },
                ),
            },
        )

        with mock_download_collection_entries(
            is_youtube_channel=is_youtube_channel, num_urls=len(season_indices)
        ):
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
            media_player_preset,
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


@pytest.mark.parametrize("music_preset", MusicPresets.preset_names)
class TestPrebuiltMusicPresets:
    def test_compilation(
        self,
        config,
        music_preset: str,
    ):
        _ = Subscription.from_dict(
            config=config,
            preset_name="preset_test",
            preset_dict={
                "preset": [
                    music_preset,
                ],
                "overrides": {
                    "music_directory": "/music",
                    "subscription_value": "https://your.name.here",
                },
            },
        )

    def test_presets_run(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        music_preset: str,
    ):
        expected_summary_name = f"unit/music/{music_preset}"

        preset_dict = {
            "preset": [
                music_preset,
            ],
            "overrides": {
                "url": "https://your.name.here",
                "music_directory": output_directory,
            },
        }

        subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=preset_dict,
        )

        num_urls = 1
        if music_preset == "SoundCloud Discography":
            num_urls = 2  # simulate /albums and /tracks

        with mock_download_collection_entries(
            is_youtube_channel=False, num_urls=num_urls, is_extracted_audio=True
        ):
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
