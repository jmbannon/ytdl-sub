from pathlib import Path
from tempfile import NamedTemporaryFile

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
def split_timestamps_file_path():
    timestamps = [
        "0:00 Intro\n",
        "00:15 Part 1\n",
        "1:01 Part 2\n",
        "01:24 Part 3\n",
        "0:02:01 Part 4\n",
        "00:02:33 Part 5\n",
    ]

    with NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".txt") as tmp:
        tmp.writelines(timestamps)
        tmp.seek(0)
        yield tmp.name


@pytest.fixture
def subscription_name():
    return "jmc"


@pytest.fixture
def config(config_path):
    return ConfigFile.from_file_path(config_path=config_path)


@pytest.fixture
def subscription_dict(output_directory, subscription_name, split_timestamps_file_path):
    return {
        "preset": "yt_music_video",
        "youtube": {
            "download_strategy": "split_video",
            "video_url": "https://youtube.com/watch?v=HKTNxEqsN3Q",
            "split_timestamps": split_timestamps_file_path,
        },
        # override the output directory with our fixture-generated dir
        "output_options": {
            "output_directory": output_directory,
            "file_name": "{playlist_index}.{title_sanitized}.{ext}",
        },
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
        },
    }


####################################################################################################
# SINGLE VIDEO FIXTURES


@pytest.fixture
def single_video_subscription(config, subscription_name, subscription_dict):
    single_video_preset = Preset.from_dict(
        config=config,
        preset_name=subscription_name,
        preset_dict=subscription_dict,
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

    def test_single_video_download(
        self, single_video_subscription, expected_single_video_download, output_directory
    ):
        single_video_subscription.download()
        expected_single_video_download.assert_files_exist(relative_directory=output_directory)
