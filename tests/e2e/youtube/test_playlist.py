import pytest
from conftest import assert_debug_log
from e2e.conftest import mock_run_from_cli
from e2e.expected_download import assert_expected_downloads
from e2e.expected_transaction_log import assert_transaction_log_matches

import ytdl_sub.downloaders.downloader
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def playlist_preset_dict(output_directory):
    return {
        "preset": "yt_music_video_playlist",
        "youtube": {"playlist_url": "https://youtube.com/playlist?list=PL5BC0FC26BECA5A35"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
        },
        "subtitles": {
            "subtitles_name": "{music_video_name}.{lang}.{subtitles_ext}",
            "allow_auto_generated_subtitles": True,
        },
        "overrides": {"artist": "JMC"},
    }


class TestPlaylistAsKodiMusicVideo:
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
            with assert_debug_log(
                logger=ytdl_sub.downloaders.downloader.download_logger,
                expected_message="ExistingVideoReached, stopping additional downloads",
            ):
                transaction_log = playlist_subscription.download()

            assert transaction_log.is_empty
            assert_expected_downloads(
                output_directory=output_directory,
                dry_run=dry_run,
                expected_download_summary_file_name="youtube/test_playlist.json",
            )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_playlist_download_from_cli_sub(
        self,
        preset_dict_to_subscription_yaml_generator,
        music_video_config_path,
        playlist_preset_dict,
        output_directory,
        dry_run,
    ):
        with preset_dict_to_subscription_yaml_generator(
            subscription_name="music_video_playlist_test", preset_dict=playlist_preset_dict
        ) as subscription_path:
            args = "--dry-run " if dry_run else ""
            args += f"--config {music_video_config_path} "
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
                with assert_debug_log(
                    logger=ytdl_sub.downloaders.downloader.download_logger,
                    expected_message="ExistingVideoReached, stopping additional downloads",
                ):
                    transaction_log = mock_run_from_cli(args=args)[0][1]

                assert transaction_log.is_empty
                assert_expected_downloads(
                    output_directory=output_directory,
                    dry_run=dry_run,
                    expected_download_summary_file_name="youtube/test_playlist.json",
                )
