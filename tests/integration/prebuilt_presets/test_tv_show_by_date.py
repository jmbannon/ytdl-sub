import pytest
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.prebuilt_presets.tv_show import TvShowByDatePresets
from ytdl_sub.subscriptions.subscription import Subscription


DEFAULT_SEASON_ORDERING = "upload-year"
DEFAULT_EPISODE_ORDERING = "upload-month-day"


class TestPrebuiltTVShowPresets:

    @staticmethod
    def run(
        config: ConfigFile,
        subscription_name: str,
        output_directory: str,
        tv_show_preset: str,
        season_ordering: str,
        episode_ordering: str,
        is_youtube_channel: bool = True,
        is_many_urls: bool = False,
    ):

        expected_summary_name = "integration/by-date/{}/{}/{}/is_yt_{}{}".format(
            tv_show_preset.split(" ")[0],
            season_ordering,
            episode_ordering,
            int(is_youtube_channel),
            "_many_urls" if is_many_urls else "",
        )

        preset_dict = {
            "preset": tv_show_preset,
            "overrides": {
                "url": "https://your.name.here",
                "tv_show_name": "Best Prebuilt TV Show by Date",
                "tv_show_directory": output_directory,
                "tv_show_by_date_season_ordering": season_ordering,
                "tv_show_by_date_episode_ordering": episode_ordering,
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
        reformatted_season_ordering = "upload-year"
        reformatted_episode_ordering = "download-index"

        reformatted_expected_summary_name = "integration/by-date/{}/{}/{}/is_yt_{}{}".format(
            tv_show_preset.split(" ")[0],
            reformatted_season_ordering,
            reformatted_episode_ordering,
            int(is_youtube_channel),
            "_many_urls" if is_many_urls else "",
        )

        reformatted_preset_dict = {
            "preset": tv_show_preset,
            "output_options": {
                "migrated_download_archive_name": ".ytdl-sub-{tv_show_name_sanitized}-download-archive.json"
            },
            "overrides": {
                "url": "https://your.name.here",
                "tv_show_name": "Best Prebuilt TV Show by Date",
                "tv_show_directory": output_directory,
                "tv_show_by_date_season_ordering": reformatted_season_ordering,
                "tv_show_by_date_episode_ordering": reformatted_episode_ordering,
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
                f"{expected_summary_name}_reformatted_to_{reformatted_season_ordering}.txt"
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
                season_ordering=DEFAULT_SEASON_ORDERING,
                episode_ordering=DEFAULT_EPISODE_ORDERING,
            )

    @pytest.mark.parametrize(
        "season_ordering, episode_ordering",
        [
            # upload
            ("upload-year", "upload-month-day"),
            ("upload-year", "upload-month-day-reversed"),
            ("upload-year", "download-index"),
            ("upload-year-month", "upload-day"),
            # release
            ("release-year", "release-month-day"),
            ("release-year", "release-month-day-reversed"),
            ("release-year", "download-index"),
            ("release-year-month", "release-day"),
        ]
    )
    def test_episode_ordering_presets(
        self,
        config,
        subscription_name,
        output_directory,
        mock_download_collection_entries,
        season_ordering: str,
        episode_ordering: str,
    ):

        with mock_download_collection_entries(
            is_youtube_channel=True,
        ):
            self.run(
                config=config,
                subscription_name=subscription_name,
                output_directory=output_directory,
                tv_show_preset="Kodi TV Show by Date",
                season_ordering=season_ordering,
                episode_ordering=episode_ordering,
            )
