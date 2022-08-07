from pathlib import Path

import pytest
from conftest import assert_debug_log
from e2e.conftest import mock_run_from_cli
from e2e.expected_download import ExpectedDownloadFile
from e2e.expected_download import ExpectedDownloads
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
        "overrides": {"artist": "JMC"},
    }


@pytest.fixture
def expected_playlist_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownloads(
        expected_downloads=[
            # Download mapping
            ExpectedDownloadFile(path=Path(".ytdl-sub-music_video_playlist_test-download-archive.json"), md5="9f785c29194a6ecfba6a6b4018763ddc"),

            # Entry files
            ExpectedDownloadFile(path=Path("JMC - Jesse's Minecraft Server [Trailer - Feb.1]-thumb.jpg"), md5="b232d253df621aa770b780c1301d364d"),
            ExpectedDownloadFile(path=Path("JMC - Jesse's Minecraft Server [Trailer - Feb.1].mp4"), md5="e66287b9832277b6a4d1554e29d9fdcc"),
            ExpectedDownloadFile(path=Path("JMC - Jesse's Minecraft Server [Trailer - Feb.1].nfo"), md5="3d272fe58487b6011ad049b6000b046f"),

            ExpectedDownloadFile(path=Path("JMC - Jesse's Minecraft Server [Trailer - Feb.27]-thumb.jpg"), md5="d17c379ea8b362f5b97c6b213b0342cb"),
            ExpectedDownloadFile(path=Path("JMC - Jesse's Minecraft Server [Trailer - Feb.27].mp4"), md5="04ab5cb3cc12325d0c96a7cd04a8b91d"),
            ExpectedDownloadFile(path=Path("JMC - Jesse's Minecraft Server [Trailer - Feb.27].nfo"), md5="6f99af10bef67276a507d1d9770c5e92"),

            ExpectedDownloadFile(path=Path("JMC - Jesse's Minecraft Server [Trailer - Mar.21]-thumb.jpg"), md5="e7830aa8a64b0cde65ba3f7e5fc56530"),
            ExpectedDownloadFile(path=Path("JMC - Jesse's Minecraft Server [Trailer - Mar.21].mp4"), md5="025de6099a5c98e6397153c7a62d517d"),
            ExpectedDownloadFile(path=Path("JMC - Jesse's Minecraft Server [Trailer - Mar.21].nfo"), md5="beec3c1326654bd8c858cecf4e40977a"),
        ]
    )
    # fmt: on


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
        expected_playlist_download,
        output_directory,
        dry_run,
    ):
        playlist_subscription = Subscription.from_dict(
            config=music_video_config,
            preset_name="music_video_playlist_test",
            preset_dict=playlist_preset_dict,
        )

        transaction_log = playlist_subscription.download()
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_playlist.txt",
        )

        if not dry_run:
            expected_playlist_download.assert_files_exist(relative_directory=output_directory)

            # Ensure another invocation will hit ExistingVideoReached
            with assert_debug_log(
                logger=ytdl_sub.downloaders.downloader.download_logger,
                expected_message="ExistingVideoReached, stopping additional downloads",
            ):
                transaction_log = playlist_subscription.download()
                expected_playlist_download.assert_files_exist(relative_directory=output_directory)
                assert transaction_log.is_empty

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_playlist_download_from_cli_sub(
        self,
        preset_dict_to_subscription_yaml_generator,
        music_video_config_path,
        playlist_preset_dict,
        expected_playlist_download,
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

            if not dry_run:
                expected_playlist_download.assert_files_exist(relative_directory=output_directory)

                # Ensure another invocation will hit ExistingVideoReached
                with assert_debug_log(
                    logger=ytdl_sub.downloaders.downloader.download_logger,
                    expected_message="ExistingVideoReached, stopping additional downloads",
                ):
                    transaction_log = mock_run_from_cli(args=args)[0][1]
                    expected_playlist_download.assert_files_exist(
                        relative_directory=output_directory
                    )
                    assert transaction_log.is_empty
