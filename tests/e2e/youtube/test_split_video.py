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
        "00:10 Part 1\n",
        "0:20 Part 2\n",
        "00:30 Part 3\n",
        "0:00:40 Part 4\n",
        "00:01:01 Part 5\n",
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
            "file_name": "{channel_sanitized} - {playlist_index}-{playlist_size}"
            ".{title_sanitized}.{ext}",
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
            Path('Project Zombie - 1-6.Intro.mp4'): "eaec6f50f364b13ef1a201e736ec9c05",
            Path('Project Zombie - 2-6.Part 1.mp4'): "5850b19acb250cc13db36f80fa1bba5a",
            Path('Project Zombie - 3-6.Part 2.mp4'): "445d95eba437db6df284df7e1ab633e8",
            Path('Project Zombie - 4-6.Part 3.mp4'): "2b6e7532d515c9e64ed2a33d850cf199",
            Path('Project Zombie - 5-6.Part 4.mp4'): "842bf3c4d1fcc4c5ab110635935dac66",
            Path('Project Zombie - 6-6.Part 5.mp4'): "238de99f00f829ab72f042b79da9a33a",
            Path('Project Zombie - Intro-thumb.jpg'): "fb95b510681676e81c321171fc23143e",
            Path('Project Zombie - Intro.nfo'): "ded59ac906f579312cc3cf98a57e7ea3",
            Path('Project Zombie - Part 1-thumb.jpg'): "fb95b510681676e81c321171fc23143e",
            Path('Project Zombie - Part 1.nfo'): "70ff5cd0092b8bc22dc4db93a824789b",
            Path('Project Zombie - Part 2-thumb.jpg'): "fb95b510681676e81c321171fc23143e",
            Path('Project Zombie - Part 2.nfo'): "54450c18a2cbb9d6d2ee5d0a1fb3f279",
            Path('Project Zombie - Part 3-thumb.jpg'): "fb95b510681676e81c321171fc23143e",
            Path('Project Zombie - Part 3.nfo'): "0effb13fc4039363a95969d1048dde57",
            Path('Project Zombie - Part 4-thumb.jpg'): "fb95b510681676e81c321171fc23143e",
            Path('Project Zombie - Part 4.nfo'): "74bd0d7c12105469838768a0cc323a8c",
            Path('Project Zombie - Part 5-thumb.jpg'): "fb95b510681676e81c321171fc23143e",
            Path('Project Zombie - Part 5.nfo'): "a8cf2e77721335ea7c18e22734e7996c",
        }
    )
    # fmt: on


class TestPlaylistAsKodiMusicVideo:
    """
    Downloads my old minecraft youtube channel, pretends they are music videos. Ensure the above
    files exist and have the expected md5 file hashes.
    """

    def test_split_video_download(
        self, single_video_subscription, expected_single_video_download, output_directory
    ):
        single_video_subscription.download()
        expected_single_video_download.assert_files_exist(relative_directory=output_directory)

    def test_split_video_dry_run(self, single_video_subscription, expected_single_video_download):
        transaction_log = single_video_subscription.download(dry_run=True)
        expected_single_video_download.assert_dry_run_files_logged(transaction_log=transaction_log)
