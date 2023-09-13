import pytest
from conftest import assert_logs
from e2e.conftest import mock_run_from_cli
from expected_download import assert_expected_downloads
from expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.subscriptions.subscription import Subscription


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


class TestPlaylist:
    """
    Downloads my old minecraft youtube channel, pretends they are music videos. Ensure the above
    files exist and have the expected md5 file hashes.
    """

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_playlist_download(
        self,
        music_video_config,
        playlist_preset_dict,
        output_directory,
        dry_run,
    ):
        playlist_subscription = Subscription.from_dict(
            config=music_video_config,
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
                _ = playlist_subscription.download()

            # TODO: output_directory_nfo is always rewritten, fix!
            # assert transaction_log.is_empty
            assert_expected_downloads(
                output_directory=output_directory,
                dry_run=dry_run,
                expected_download_summary_file_name="youtube/test_playlist.json",
            )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_playlist_download_from_cli_sub(
        self,
        preset_dict_to_subscription_yaml_generator,
        music_video_config_for_cli,
        playlist_preset_dict,
        output_directory,
        dry_run,
    ):
        with preset_dict_to_subscription_yaml_generator(
            subscription_name="music_video_playlist_test", preset_dict=playlist_preset_dict
        ) as subscription_path:
            args = "--dry-run " if dry_run else ""
            args += f"--config {music_video_config_for_cli} "
            args += f"sub {subscription_path}"
            subscription_transaction_log = mock_run_from_cli(args=args)

            assert len(subscription_transaction_log) == 1
            transaction_log = subscription_transaction_log[0][1]

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
                    _ = mock_run_from_cli(args=args)[0][1]

                # TODO: output_directory_nfo is always rewritten, fix!
                # assert transaction_log.is_empty
                assert_expected_downloads(
                    output_directory=output_directory,
                    dry_run=dry_run,
                    expected_download_summary_file_name="youtube/test_playlist.json",
                )
