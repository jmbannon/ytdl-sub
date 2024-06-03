from pathlib import Path
from typing import Dict

import pytest
from conftest import assert_logs
from e2e.conftest import mock_run_from_cli
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches
from mergedeep import mergedeep

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.subscriptions.subscription import Subscription
from ytdl_sub.utils.system import IS_WINDOWS


@pytest.fixture
def playlist_preset_dict(output_directory):
    return {
        "preset": [
            "jellyfin_tv_show_collection",
            "season_by_collection__episode_by_year_month_day",
            "collection_season_1",
        ],
        "format": "worst[ext=mp4]",  # download the worst format so it is fast
        "output_directory_nfo_tags": {
            "nfo_name": "tvshow.nfo",
            "nfo_root": "test",
            "tags": {
                "playlist_title": "{playlist_title}",
                "playlist_uploader": "{playlist_uploader}",
                "playlist_description": "{playlist_description}",
            },
        },
        "nfo_tags": {
            "tags": {
                "playlist_index": "{playlist_index}",
                "playlist_count": "{playlist_count}",
            }
        },
        "subtitles": {
            "subtitles_name": "{episode_file_path}.{lang}.{subtitles_ext}",
            "allow_auto_generated_subtitles": True,
        },
        "overrides": {
            "tv_show_name": "JMC",
            "tv_show_directory": output_directory,
            "collection_season_1_url": "https://youtube.com/playlist?list=PL5BC0FC26BECA5A35",
            "collection_season_1_name": "JMC - Season 1",
        },
    }


@pytest.fixture
def tv_show_by_date_bilateral_dict(output_directory):
    return {
        "preset": [
            "Jellyfin TV Show by Date",
        ],
        "format": "worst[ext=mp4]",
        "match_filters": {"filters": ["title *= Feb.1"]},
        "overrides": {
            "url": "https://www.youtube.com/playlist?list=PLd4Q7G88JqoekF0b30NYQcOTnTiIe9Ali",
            "tv_show_directory": output_directory,
        },
        "nfo_tags": {
            "tags": {
                "subscription_has_download_archive": "{subscription_has_download_archive}",
                "download_index": "{download_index}",
            }
        },
    }


@pytest.fixture
def tv_show_collection_bilateral_dict(output_directory):
    return {
        "preset": [
            "Jellyfin TV Show Collection",
        ],
        "format": "worst[ext=mp4]",
        "match_filters": {"filters": ["title *= Feb.1"]},
        "overrides": {
            "s01_url": "https://www.youtube.com/playlist?list=PLd4Q7G88JqoekF0b30NYQcOTnTiIe9Ali",
            "s01_name": "bilateral test",
            "tv_show_directory": output_directory,
        },
        "nfo_tags": {
            "tags": {
                "subscription_has_download_archive": "{subscription_has_download_archive}",
                "download_index": "{download_index}",
            }
        },
    }


class TestPlaylist:
    """
    Downloads my old minecraft youtube channel, pretends they are music videos. Ensure the above
    files exist and have the expected md5 file hashes.
    """

    @classmethod
    def _ensure_subscription_migrates(
        cls,
        config: ConfigFile,
        subscription_name: str,
        subscription_dict: Dict,
        output_directory: Path,
    ):
        # Ensure download archive migrates
        mergedeep.merge(
            subscription_dict,
            {
                "output_options": {
                    "migrated_download_archive_name": ".ytdl-sub-{tv_show_name_sanitized}-download-archive.json"
                }
            },
        )
        migrated_subscription = Subscription.from_dict(
            config=config,
            preset_name=subscription_name,
            preset_dict=subscription_dict,
        )
        transaction_log = migrated_subscription.download()

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist_archive_migrated.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name="youtube/test_playlist_archive_migrated.json",
        )

        # Ensure no changes after migration
        transaction_log = migrated_subscription.download()
        assert transaction_log.is_empty
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=False,
            expected_download_summary_file_name="youtube/test_playlist_archive_migrated.json",
        )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_playlist_download(
        self,
        default_config,
        playlist_preset_dict,
        output_directory,
        dry_run,
    ):
        playlist_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="music_video_playlist_test",
            preset_dict=playlist_preset_dict,
        )

        transaction_log = playlist_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist.txt",
        )
        assert_expected_downloads(
            output_directory=output_directory,
            dry_run=dry_run,
            expected_download_summary_file_name="youtube/test_playlist.json",
        )

        # Ensure another invocation will hit ExistingVideoReached
        if not dry_run:
            with assert_logs(
                logger=YTDLP.logger,
                expected_message="ExistingVideoReached, stopping additional downloads",
                log_level="debug",
            ):
                transaction_log = playlist_subscription.download()

            assert transaction_log.is_empty
            assert_expected_downloads(
                output_directory=output_directory,
                dry_run=dry_run,
                expected_download_summary_file_name="youtube/test_playlist.json",
            )

            self._ensure_subscription_migrates(
                config=default_config,
                subscription_name="music_video_playlist_test",
                subscription_dict=playlist_preset_dict,
                output_directory=output_directory,
            )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_playlist_download_from_cli_sub_no_provided_config(
        self,
        preset_dict_to_subscription_yaml_generator,
        playlist_preset_dict,
        output_directory,
        dry_run,
    ):
        # TODO: Fix CLI parsing on windows when dealing with spaces
        if IS_WINDOWS:
            return

        # No config needed when using only prebuilt presets
        with preset_dict_to_subscription_yaml_generator(
            subscription_name="music_video_playlist_test", preset_dict=playlist_preset_dict
        ) as subscription_path:
            args = "--dry-run " if dry_run else ""
            args += f"sub '{subscription_path}'"
            subscriptions = mock_run_from_cli(args=args)

            assert len(subscriptions) == 1
            transaction_log = subscriptions[0].transaction_log

            assert_transaction_log_matches(
                output_directory=output_directory,
                transaction_log=transaction_log,
                transaction_log_summary_file_name="youtube/test_playlist.txt",
            )
            assert_expected_downloads(
                output_directory=output_directory,
                dry_run=dry_run,
                expected_download_summary_file_name="youtube/test_playlist.json",
            )

            if not dry_run:
                # Ensure another invocation will hit ExistingVideoReached
                with assert_logs(
                    logger=YTDLP.logger,
                    expected_message="ExistingVideoReached, stopping additional downloads",
                    log_level="debug",
                ):
                    transaction_log = mock_run_from_cli(args=args)[0].transaction_log

                assert transaction_log.is_empty
                assert_expected_downloads(
                    output_directory=output_directory,
                    dry_run=dry_run,
                    expected_download_summary_file_name="youtube/test_playlist.json",
                )

    def test_playlist_download_from_cli_sub_with_override_arg(
        self,
        preset_dict_to_subscription_yaml_generator,
        playlist_preset_dict,
        output_directory,
    ):
        # TODO: Fix CLI parsing on windows when dealing with spaces
        if IS_WINDOWS:
            return

        # No config needed when using only prebuilt presets
        with preset_dict_to_subscription_yaml_generator(
            subscription_name="music_video_playlist_test", preset_dict=playlist_preset_dict
        ) as subscription_path:
            args = (
                f"--dry-run sub '{subscription_path}' --dl-override '--date_range.after 20240101'"
            )

            subscriptions = mock_run_from_cli(args=args)

            assert len(subscriptions) == 1
            assert subscriptions[0].transaction_log.is_empty

    def test_tv_show_by_date_downloads_bilateral(
        self,
        tv_show_by_date_bilateral_dict: Dict,
        output_directory: str,
        default_config: ConfigFile,
    ):
        playlist_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="bilateral_test",
            preset_dict=tv_show_by_date_bilateral_dict,
        )

        transaction_log = playlist_subscription.download(dry_run=False)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist_bilateral_p1.txt",
        )

        # Now that one vid is downloaded, attempt to download all and see if bilateral
        # logic kicks in
        del tv_show_by_date_bilateral_dict["match_filters"]
        playlist_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="bilateral_test",
            preset_dict=tv_show_by_date_bilateral_dict,
        )
        transaction_log = playlist_subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist_bilateral_p2.txt",
        )

    def test_tv_show_collection_downloads_bilateral(
        self,
        tv_show_collection_bilateral_dict: Dict,
        output_directory: str,
        default_config: ConfigFile,
    ):
        playlist_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="bilateral_test",
            preset_dict=tv_show_collection_bilateral_dict,
        )

        transaction_log = playlist_subscription.download(dry_run=False)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist_bilateral_collection_p1.txt",
        )

        # Now that one vid is downloaded, attempt to download all and see if bilateral
        # logic kicks in
        del tv_show_collection_bilateral_dict["match_filters"]
        playlist_subscription = Subscription.from_dict(
            config=default_config,
            preset_name="bilateral_test",
            preset_dict=tv_show_collection_bilateral_dict,
        )
        transaction_log = playlist_subscription.download(dry_run=True)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist_bilateral_collection_p2.txt",
        )
