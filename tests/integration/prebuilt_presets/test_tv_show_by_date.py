import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.prebuilt_presets.tv_show import TvShowByDateEpisodeFormattingPresets
from ytdl_sub.prebuilt_presets.tv_show import TvShowByDatePresets
from ytdl_sub.subscriptions.subscription import Subscription

DEPRECATED_TV_SHOW_PRESET_EQUIVALENTS = {
    "Kodi TV Show by Date": "kodi_tv_show_by_date",
    "Jellyfin TV Show by Date": "jellyfin_tv_show_by_date",
    "Plex TV Show by Date": "plex_tv_show_by_date",
}

DEFAULT_EPISODE_ORDERING_PRESET = "season_by_year__episode_by_month_day"


class TestPrebuiltTVShowPresets:

    @staticmethod
    def run(
        config: ConfigFile,
        subscription_name: str,
        output_directory: str,
        tv_show_preset: str,
        episode_ordering_preset: str,
        is_youtube_channel: bool = True,
        is_many_urls: bool = False,
    ):

        expected_summary_name = "unit/{}/{}/is_yt_{}{}".format(
            DEPRECATED_TV_SHOW_PRESET_EQUIVALENTS[tv_show_preset],
            episode_ordering_preset,
            int(is_youtube_channel),
            "_many_urls" if is_many_urls else "",
        )

        preset_dict = {
            "preset": [tv_show_preset, episode_ordering_preset],
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
            DEPRECATED_TV_SHOW_PRESET_EQUIVALENTS[tv_show_preset],
            reformatted_tv_show_structure_preset,
            int(is_youtube_channel),
            "_many_urls" if is_many_urls else "",
        )

        reformatted_preset_dict = {
            "preset": [tv_show_preset, reformatted_tv_show_structure_preset],
            "output_options": {
                "migrated_download_archive_name": ".ytdl-sub-{tv_show_name_sanitized}-download-archive.json"
            },
            "overrides": {
                "url": "https://your.name.here",
                "tv_show_name": "Best Prebuilt TV Show by Date",
                "tv_show_directory": output_directory,
            },
        }
        if is_many_urls:
            reformatted_preset_dict["overrides"]["url2"] = "https://url.number.2.here"

        reformatted_subscription = Subscription.from_dict(
            config=config, preset_name=subscription_name, preset_dict=reformatted_preset_dict
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

    @pytest.mark.parametrize("tv_show_preset", TvShowByDatePresets.preset_names)
    def test_tv_show_presets(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        tv_show_preset: str,
    ):

        with mock_download_collection_entries(is_youtube_channel=True):
            self.run(
                config=config,
                subscription_name=subscription_name,
                output_directory=output_directory,
                tv_show_preset=tv_show_preset,
                episode_ordering_preset=DEFAULT_EPISODE_ORDERING_PRESET,
            )

    @pytest.mark.parametrize(
        "episode_ordering_preset", TvShowByDateEpisodeFormattingPresets.preset_names
    )
    def test_episode_ordering_presets(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        episode_ordering_preset: str,
    ):

        with mock_download_collection_entries(
            is_youtube_channel=True,
        ):
            self.run(
                config=config,
                subscription_name=subscription_name,
                output_directory=output_directory,
                tv_show_preset="Kodi TV Show by Date",
                episode_ordering_preset=episode_ordering_preset,
            )
