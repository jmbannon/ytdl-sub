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
            Path(".ytdl-sub-jmc-download-archive.json"): "7541aa75606b86bff5ff276895520cf0",

            # Entry files
            Path("JMC - Jesse's Minecraft Server [Trailer - Feb.1].jpg"): "048a19cf0f674437351872c3f312ebf1",
            Path("JMC - Jesse's Minecraft Server [Trailer - Feb.1].mp4"): "e66287b9832277b6a4d1554e29d9fdcc",
            Path("JMC - Jesse's Minecraft Server [Trailer - Feb.1].nfo"): "3d272fe58487b6011ad049b6000b046f",

            Path("JMC - Given to Fly.jpg"): "2e58e4d5f06ce5d1c3336fa493470135",
            Path("JMC - Given to Fly.mp4"): "04ab5cb3cc12325d0c96a7cd04a8b91d",
            Path("JMC - Given to Fly.nfo"): "0dc578bf5f1ceb6e069a57d329894f35",

            Path("JMC - Indifference (Remastered).jpg"): "9baaddc6b62f5b9ae3781eb4eef0e3b3",
            Path("JMC - Indifference (Remastered).mp4"): "025de6099a5c98e6397153c7a62d517d",
            Path("JMC - Indifference (Remastered).nfo"): "061b86d9dc8fb39d39feab3292dafeb0",
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
            Path("JMC - Whale & Wasp.jpg"): "b58377dfe7c39527e1990a24b36bbd77",
            Path("JMC - Whale & Wasp.mp4"): "931a705864c57d21d6fedebed4af6bbc",
            Path("JMC - Whale & Wasp.nfo"): "6c2f085adb847c1dcc47c19514c454d8",
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

    def test_single_video_download(
        self, single_video_subscription, expected_single_video_download, output_directory
    ):
        single_video_subscription.download()
        expected_single_video_download.assert_files_exist(relative_directory=output_directory)
