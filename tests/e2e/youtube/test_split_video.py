from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from e2e.expected_download import ExpectedDownloadFile
from e2e.expected_download import ExpectedDownloads
from e2e.expected_transaction_log import assert_transaction_log_matches

from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def subscription_dict(output_directory, timestamps_file_path):
    return {
        "preset": "yt_music_video",
        "youtube": {
            "download_strategy": "split_video",
            "video_url": "https://youtube.com/watch?v=HKTNxEqsN3Q",
            "split_timestamps": timestamps_file_path,
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
def single_video_subscription(music_video_config, subscription_dict):
    single_video_preset = Preset.from_dict(
        config=music_video_config,
        preset_name="split_video_test",
        preset_dict=subscription_dict,
    )

    return Subscription.from_preset(
        preset=single_video_preset,
        config=music_video_config,
    )


@pytest.fixture
def expected_single_video_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownloads(
        expected_downloads=[
            ExpectedDownloadFile(path=Path('Project Zombie - 1-6.Intro.mp4'), md5="eaec6f50f364b13ef1a201e736ec9c05"),
            ExpectedDownloadFile(path=Path('Project Zombie - 2-6.Part 1.mp4'), md5="5850b19acb250cc13db36f80fa1bba5a"),
            ExpectedDownloadFile(path=Path('Project Zombie - 3-6.Part 2.mp4'), md5="445d95eba437db6df284df7e1ab633e8"),
            ExpectedDownloadFile(path=Path('Project Zombie - 4-6.Part 3.mp4'), md5="2b6e7532d515c9e64ed2a33d850cf199"),
            ExpectedDownloadFile(path=Path('Project Zombie - 5-6.Part 4.mp4'), md5="842bf3c4d1fcc4c5ab110635935dac66"),
            ExpectedDownloadFile(path=Path('Project Zombie - 6-6.Part 5.mp4'), md5="238de99f00f829ab72f042b79da9a33a"),
            ExpectedDownloadFile(path=Path('Project Zombie - Intro-thumb.jpg'), md5="fb95b510681676e81c321171fc23143e"),
            ExpectedDownloadFile(path=Path('Project Zombie - Intro.nfo'), md5="ded59ac906f579312cc3cf98a57e7ea3"),
            ExpectedDownloadFile(path=Path('Project Zombie - Part 1-thumb.jpg'), md5="fb95b510681676e81c321171fc23143e"),
            ExpectedDownloadFile(path=Path('Project Zombie - Part 1.nfo'), md5="70ff5cd0092b8bc22dc4db93a824789b"),
            ExpectedDownloadFile(path=Path('Project Zombie - Part 2-thumb.jpg'), md5="fb95b510681676e81c321171fc23143e"),
            ExpectedDownloadFile(path=Path('Project Zombie - Part 2.nfo'), md5="54450c18a2cbb9d6d2ee5d0a1fb3f279"),
            ExpectedDownloadFile(path=Path('Project Zombie - Part 3-thumb.jpg'), md5="fb95b510681676e81c321171fc23143e"),
            ExpectedDownloadFile(path=Path('Project Zombie - Part 3.nfo'), md5="0effb13fc4039363a95969d1048dde57"),
            ExpectedDownloadFile(path=Path('Project Zombie - Part 4-thumb.jpg'), md5="fb95b510681676e81c321171fc23143e"),
            ExpectedDownloadFile(path=Path('Project Zombie - Part 4.nfo'), md5="74bd0d7c12105469838768a0cc323a8c"),
            ExpectedDownloadFile(path=Path('Project Zombie - Part 5-thumb.jpg'), md5="fb95b510681676e81c321171fc23143e"),
            ExpectedDownloadFile(path=Path('Project Zombie - Part 5.nfo'), md5="a8cf2e77721335ea7c18e22734e7996c"),
        ]
    )
    # fmt: on


class TestPlaylistAsKodiMusicVideo:
    """
    Downloads my old minecraft youtube channel, pretends they are music videos. Ensure the above
    files exist and have the expected md5 file hashes.
    """

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_split_video_download(
        self, single_video_subscription, expected_single_video_download, output_directory, dry_run
    ):
        transaction_log = single_video_subscription.download()
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_split_video.txt",
        )

        if not dry_run:
            expected_single_video_download.assert_files_exist(relative_directory=output_directory)
