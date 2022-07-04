from pathlib import Path

import mergedeep
import pytest
from conftest import assert_debug_log
from e2e.expected_download import ExpectedDownload

import ytdl_sub.downloaders.downloader
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def config_path():
    return "examples/kodi_music_videos_config.yaml"


@pytest.fixture
def subscription_name():
    return "jmc"


@pytest.fixture
def config(config_path):
    return ConfigFile.from_file_path(config_path=config_path)


@pytest.fixture
def subscription_dict(output_directory, subscription_name):
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


####################################################################################################
# PLAYLIST FIXTURES


@pytest.fixture
def playlist_subscription(config, subscription_name, subscription_dict):
    playlist_preset = Preset.from_dict(
        config=config,
        preset_name=subscription_name,
        preset_dict=subscription_dict,
    )

    return Subscription.from_preset(
        preset=playlist_preset,
        config=config,
    )


@pytest.fixture
def expected_playlist_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownload(
        expected_md5_file_hashes={
            # Download mapping
            Path(".ytdl-sub-jmc-download-archive.json"): "9f785c29194a6ecfba6a6b4018763ddc",

            # Entry files
            Path("JMC - Jesse's Minecraft Server [Trailer - Feb.1]-thumb.jpg"): "b232d253df621aa770b780c1301d364d",
            Path("JMC - Jesse's Minecraft Server [Trailer - Feb.1].mp4"): "e66287b9832277b6a4d1554e29d9fdcc",
            Path("JMC - Jesse's Minecraft Server [Trailer - Feb.1].nfo"): "3d272fe58487b6011ad049b6000b046f",

            Path("JMC - Jesse's Minecraft Server [Trailer - Feb.27]-thumb.jpg"): "d17c379ea8b362f5b97c6b213b0342cb",
            Path("JMC - Jesse's Minecraft Server [Trailer - Feb.27].mp4"): "04ab5cb3cc12325d0c96a7cd04a8b91d",
            Path("JMC - Jesse's Minecraft Server [Trailer - Feb.27].nfo"): "6f99af10bef67276a507d1d9770c5e92",

            Path("JMC - Jesse's Minecraft Server [Trailer - Mar.21]-thumb.jpg"): "e7830aa8a64b0cde65ba3f7e5fc56530",
            Path("JMC - Jesse's Minecraft Server [Trailer - Mar.21].mp4"): "025de6099a5c98e6397153c7a62d517d",
            Path("JMC - Jesse's Minecraft Server [Trailer - Mar.21].nfo"): "beec3c1326654bd8c858cecf4e40977a",
        }
    )
    # fmt: on


####################################################################################################
# SINGLE VIDEO FIXTURES
@pytest.fixture
def single_video_subscription_dict(subscription_dict):
    del subscription_dict["youtube"]

    return mergedeep.merge(
        subscription_dict,
        {
            "preset": "yt_music_video",
            "youtube": {"video_url": "https://youtube.com/watch?v=HKTNxEqsN3Q"},
        },
    )


@pytest.fixture
def single_video_subscription(config, subscription_name, single_video_subscription_dict):
    single_video_preset = Preset.from_dict(
        config=config,
        preset_name=subscription_name,
        preset_dict=single_video_subscription_dict,
    )

    return Subscription.from_preset(
        preset=single_video_preset,
        config=config,
    )


@pytest.fixture
def expected_single_video_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownload(
        expected_md5_file_hashes={
            Path("JMC - Oblivion Mod 'Falcor' p.1-thumb.jpg"): "fb95b510681676e81c321171fc23143e",
            Path("JMC - Oblivion Mod 'Falcor' p.1.mp4"): "931a705864c57d21d6fedebed4af6bbc",
            Path("JMC - Oblivion Mod 'Falcor' p.1.nfo"): "89f509a8a3d9003e22a9091abeeae5dc",
        }
    )
    # fmt: on


class TestPlaylistAsKodiMusicVideo:
    """
    Downloads my old minecraft youtube channel, pretends they are music videos. Ensure the above
    files exist and have the expected md5 file hashes.
    """

    def test_playlist_download(
        self, playlist_subscription, expected_playlist_download, output_directory
    ):
        playlist_subscription.download()
        expected_playlist_download.assert_files_exist(relative_directory=output_directory)

        # After the playlist is downloaded, ensure another invocation will hit ExistingVideoReached
        with assert_debug_log(
            logger=ytdl_sub.downloaders.downloader.logger,
            expected_message="ExistingVideoReached, stopping additional downloads",
        ):
            playlist_subscription.download()
            expected_playlist_download.assert_files_exist(relative_directory=output_directory)

    def test_playlist_dry_run(
        self, playlist_subscription, expected_playlist_download, output_directory
    ):
        file_transaction_log = playlist_subscription.download(dry_run=True)
        expected_playlist_download.assert_dry_run_files_logged(transaction_log=file_transaction_log)

    def test_single_video_download(
        self, single_video_subscription, expected_single_video_download, output_directory
    ):
        single_video_subscription.download()
        expected_single_video_download.assert_files_exist(relative_directory=output_directory)

    def test_single_video_dry_run(
        self, single_video_subscription, expected_single_video_download, output_directory
    ):
        file_transaction_log = single_video_subscription.download(dry_run=True)
        expected_single_video_download.assert_dry_run_files_logged(
            transaction_log=file_transaction_log
        )
