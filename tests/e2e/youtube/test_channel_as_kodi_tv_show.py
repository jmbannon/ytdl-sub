import copy
from pathlib import Path
from typing import Dict

import mergedeep
import pytest
from conftest import assert_debug_log
from e2e.expected_download import ExpectedDownloadFile
from e2e.expected_download import ExpectedDownloads
from e2e.expected_transaction_log import assert_transaction_log_matches

import ytdl_sub.downloaders.downloader
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def subscription_name():
    return "pz"


@pytest.fixture
def channel_preset_dict(output_directory):
    return {
        "preset": "yt_channel_as_tv",
        "youtube": {"channel_url": "https://youtube.com/channel/UCcRSMoQqXc_JrBZRHDFGbqA"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": output_directory},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
            "max_views": 100000,  # do not download the popular PJ concert
            "break_on_reject": False,  # do not break from max views
        },
        "overrides": {"tv_show_name": "Project / Zombie"},
    }


@pytest.fixture
def channel_subscription_generator(channel_as_tv_show_config, subscription_name):
    def _channel_subscription_generator(preset_dict: Dict):
        return Subscription.from_dict(
            config=channel_as_tv_show_config, preset_name=subscription_name, preset_dict=preset_dict
        )

    return _channel_subscription_generator


####################################################################################################
# FULL CHANNEL FIXTURES


@pytest.fixture
def expected_full_channel_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownloads(
        expected_downloads=[
            # Download mapping
            ExpectedDownloadFile(path=Path(".ytdl-sub-pz-download-archive.json"), md5="dd3c6236a107a665b884f701b8d14d4d"),

            # Output directory files
            ExpectedDownloadFile(path=Path("fanart.jpg"), md5="c16b8b88a82cbd47d217ee80f6a8b5f3"),
            ExpectedDownloadFile(path=Path("poster.jpg"), md5="e92872ff94c96ad49e9579501c791578"),
            ExpectedDownloadFile(path=Path("tvshow.nfo"), md5="83c7db96081ac5bdf289fcf396bec157"),

            # Entry files
            ExpectedDownloadFile(path=Path("Season 2010/s2010.e0813 - Oblivion Mod 'Falcor' p.1-thumb.jpg"), md5="fb95b510681676e81c321171fc23143e"),
            ExpectedDownloadFile(path=Path("Season 2010/s2010.e0813 - Oblivion Mod 'Falcor' p.1.mp4"), md5="931a705864c57d21d6fedebed4af6bbc"),
            ExpectedDownloadFile(path=Path("Season 2010/s2010.e0813 - Oblivion Mod 'Falcor' p.1.nfo"), md5="67d8d71d048039080acbba3bce4febaa"),

            ExpectedDownloadFile(path=Path("Season 2010/s2010.e1202 - Oblivion Mod 'Falcor' p.2-thumb.jpg"), md5="8b32ee9c037fa669e444a0ac181525a1"),
            ExpectedDownloadFile(path=Path("Season 2010/s2010.e1202 - Oblivion Mod 'Falcor' p.2.mp4"), md5="d3469b4dca7139cb3dbc38712b6796bf"),
            ExpectedDownloadFile(path=Path("Season 2010/s2010.e1202 - Oblivion Mod 'Falcor' p.2.nfo"), md5="d81f49cedbd7edaee987521e89b37904"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0201 - Jesse's Minecraft Server [Trailer - Feb.1]-thumb.jpg"), md5="b232d253df621aa770b780c1301d364d"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0201 - Jesse's Minecraft Server [Trailer - Feb.1].mp4"), md5="e66287b9832277b6a4d1554e29d9fdcc"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0201 - Jesse's Minecraft Server [Trailer - Feb.1].nfo"), md5="f7c0de89038f8c491bded8a3968720a2"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0227 - Jesse's Minecraft Server [Trailer - Feb.27]-thumb.jpg"), md5="d17c379ea8b362f5b97c6b213b0342cb"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0227 - Jesse's Minecraft Server [Trailer - Feb.27].mp4"), md5="04ab5cb3cc12325d0c96a7cd04a8b91d"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0227 - Jesse's Minecraft Server [Trailer - Feb.27].nfo"), md5="ee1eda78fa0980bc703e602b5012dd1f"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0321 - Jesse's Minecraft Server [Trailer - Mar.21]-thumb.jpg"), md5="e7830aa8a64b0cde65ba3f7e5fc56530"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0321 - Jesse's Minecraft Server [Trailer - Mar.21].mp4"), md5="025de6099a5c98e6397153c7a62d517d"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0321 - Jesse's Minecraft Server [Trailer - Mar.21].nfo"), md5="61eb6369430da0ab6134d78829a7621b"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0529 - Project Zombie _Official Trailer_ (IP - mc.projectzombie.beastnode.net)-thumb.jpg"), md5="c956192a379b3661595c9920972d4819"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0529 - Project Zombie _Official Trailer_ (IP - mc.projectzombie.beastnode.net).mp4"), md5="3d9c19835b03355d6fd5d00cd59dbe5b"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0529 - Project Zombie _Official Trailer_ (IP - mc.projectzombie.beastnode.net).nfo"), md5="60f72b99f5c69f9e03a071a12160928f"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0630 - Project Zombie _Fin-thumb.jpg"), md5="00ed383591779ffe98291de60f198fe9"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0630 - Project Zombie _Fin.mp4"), md5="4971cb2d4fa29460361031f3fa8e1ea9"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0630 - Project Zombie _Fin.nfo"), md5="a7b5d9e57d20852f5daf360a1373bb7a"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e1121 - Skyrim 'Ultra HD w_Mods' [PC]-thumb.jpg"), md5="1718599d5189c65f7d8cf6acfa5ea851"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e1121 - Skyrim 'Ultra HD w_Mods' [PC].mp4"), md5="55e9b0add08c48c9c66105da0def2426"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e1121 - Skyrim 'Ultra HD w_Mods' [PC].nfo"), md5="fe60e2b6b564f9316b6c7c183e1cf300"),

            ExpectedDownloadFile(path=Path("Season 2012/s2012.e0123 - Project Zombie _Map Trailer-thumb.jpg"), md5="54ebe9df801b278fdd17b21afa8373a6"),
            ExpectedDownloadFile(path=Path("Season 2012/s2012.e0123 - Project Zombie _Map Trailer.mp4"), md5="65e4ce53ed5ec4139995469f99477a50"),
            ExpectedDownloadFile(path=Path("Season 2012/s2012.e0123 - Project Zombie _Map Trailer.nfo"), md5="c8900adcca83c473c79a4afbc7ad2de1"),

            ExpectedDownloadFile(path=Path("Season 2013/s2013.e0719 - Project Zombie Rewind _Trailer-thumb.jpg"), md5="e29d49433175de8a761af35c5307791f"),
            ExpectedDownloadFile(path=Path("Season 2013/s2013.e0719 - Project Zombie Rewind _Trailer.mp4"), md5="18620a8257a686beda65e54add4d4cd1"),
            ExpectedDownloadFile(path=Path("Season 2013/s2013.e0719 - Project Zombie Rewind _Trailer.nfo"), md5="1c993c41d4308a6049333154d0adee16"),

            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer-thumb.jpg"), md5="6f8f5e1e031ec2a04b0a4906c04a19ee"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.mp4"), md5="82f6ee7253e1dbb83ae7215af08ffacc"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.nfo"), md5="cc7886aae3af6b7b0facd82f95390242"),

            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id-thumb.jpg"), md5="49cc64b25314155c1b8ab0361ac0c34f"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.mp4"), md5="e733b4cc385b953b08c8eb0f47e03c1e"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.nfo"), md5="2b3ccb3f1ef81ee49fe1afb88f275a09"),
        ]
    )
    # fmt: on


####################################################################################################
# RECENT CHANNEL FIXTURES
@pytest.fixture
def recent_channel_preset_dict(channel_preset_dict):
    # TODO: remove this hack by using a different channel
    channel_preset_dict = copy.deepcopy(channel_preset_dict)
    del channel_preset_dict["ytdl_options"]["break_on_reject"]
    return mergedeep.merge(
        channel_preset_dict,
        {
            "preset": "yt_channel_as_tv__recent",
            "youtube": {"after": "20150101"},
        },
    )


@pytest.fixture
def expected_recent_channel_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownloads(
        expected_downloads=[
            # Download mapping
            ExpectedDownloadFile(path=Path(".ytdl-sub-pz-download-archive.json"), md5="91534d1c5921d121aa35d7a197ba1940"),

            # Output directory files
            ExpectedDownloadFile(path=Path("fanart.jpg"), md5="c16b8b88a82cbd47d217ee80f6a8b5f3"),
            ExpectedDownloadFile(path=Path("poster.jpg"), md5="e92872ff94c96ad49e9579501c791578"),
            ExpectedDownloadFile(path=Path("tvshow.nfo"), md5="83c7db96081ac5bdf289fcf396bec157"),

            # Recent Entry files
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer-thumb.jpg"), md5="6f8f5e1e031ec2a04b0a4906c04a19ee"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.mp4"), md5="82f6ee7253e1dbb83ae7215af08ffacc"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.nfo"), md5="cc7886aae3af6b7b0facd82f95390242"),

            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id-thumb.jpg"), md5="49cc64b25314155c1b8ab0361ac0c34f"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.mp4"), md5="e733b4cc385b953b08c8eb0f47e03c1e"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.nfo"), md5="2b3ccb3f1ef81ee49fe1afb88f275a09"),
        ]
    )
    # fmt: on


####################################################################################################
# RECENT CHANNEL FIXTURES -- NO VIDS IN RANGE


@pytest.fixture
def expected_recent_channel_no_vids_in_range_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownloads(
        expected_downloads=[
            # Download mapping
            ExpectedDownloadFile(path=Path(".ytdl-sub-pz-download-archive.json"), md5="99914b932bd37a50b983c5e7c90ae93b"),

            # Output directory files
            ExpectedDownloadFile(path=Path("fanart.jpg"), md5="c16b8b88a82cbd47d217ee80f6a8b5f3"),
            ExpectedDownloadFile(path=Path("poster.jpg"), md5="e92872ff94c96ad49e9579501c791578"),
            ExpectedDownloadFile(path=Path("tvshow.nfo"), md5="83c7db96081ac5bdf289fcf396bec157"),
        ]
    )
    # fmt: on


####################################################################################################
# ROLLING RECENT CHANNEL FIXTURES
@pytest.fixture
def rolling_recent_channel_preset_dict(recent_channel_preset_dict):
    recent_channel_preset_dict = copy.deepcopy(recent_channel_preset_dict)
    return mergedeep.merge(
        recent_channel_preset_dict,
        {
            "preset": "yt_channel_as_tv__only_recent",
            "output_options": {"keep_files_after": "20181101"},
        },
    )


@pytest.fixture
def expected_rolling_recent_channel_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownloads(
        expected_downloads=[
            # Download mapping
            ExpectedDownloadFile(path=Path(".ytdl-sub-pz-download-archive.json"), md5="97ff47a7c5d89a426a653493ad1a3f06"),

            # Output directory files
            ExpectedDownloadFile(path=Path("fanart.jpg"), md5="c16b8b88a82cbd47d217ee80f6a8b5f3"),
            ExpectedDownloadFile(path=Path("poster.jpg"), md5="e92872ff94c96ad49e9579501c791578"),
            ExpectedDownloadFile(path=Path("tvshow.nfo"), md5="83c7db96081ac5bdf289fcf396bec157"),

            # Rolling Recent Entry files
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id-thumb.jpg"), md5="49cc64b25314155c1b8ab0361ac0c34f"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.mp4"), md5="e733b4cc385b953b08c8eb0f47e03c1e"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.nfo"), md5="2b3ccb3f1ef81ee49fe1afb88f275a09"),
        ]
    )
    # fmt: on


class TestChannelAsKodiTvShow:
    """
    Downloads my old minecraft youtube channel. Ensure the above files exist and have the
    expected md5 file hashes.
    """

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_full_channel_download(
        self,
        channel_subscription_generator,
        channel_preset_dict,
        expected_full_channel_download,
        output_directory,
        dry_run,
    ):
        full_channel_subscription = channel_subscription_generator(preset_dict=channel_preset_dict)
        transaction_log = full_channel_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_channel_full.txt",
        )
        if not dry_run:
            expected_full_channel_download.assert_files_exist(relative_directory=output_directory)

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_recent_channel_download(
        self,
        channel_subscription_generator,
        recent_channel_preset_dict,
        expected_recent_channel_download,
        output_directory,
        dry_run,
    ):
        recent_channel_subscription = channel_subscription_generator(
            preset_dict=recent_channel_preset_dict
        )

        transaction_log = recent_channel_subscription.download(dry_run=dry_run)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_channel_recent.txt",
        )
        if not dry_run:
            expected_recent_channel_download.assert_files_exist(relative_directory=output_directory)

            # try downloading again, ensure nothing more was downloaded
            with assert_debug_log(
                logger=ytdl_sub.downloaders.downloader.download_logger,
                expected_message="ExistingVideoReached, stopping additional downloads",
            ):
                transaction_log = recent_channel_subscription.download()
                assert_transaction_log_matches(
                    output_directory=output_directory,
                    transaction_log=transaction_log,
                    transaction_log_summary_file_name=(
                        "youtube/test_channel_no_additional_downloads.txt"
                    ),
                )
                expected_recent_channel_download.assert_files_exist(
                    relative_directory=output_directory
                )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_recent_channel_download__no_vids_in_range(
        self,
        channel_subscription_generator,
        recent_channel_preset_dict,
        expected_recent_channel_no_vids_in_range_download,
        output_directory,
        dry_run,
    ):
        recent_channel_preset_dict["youtube"]["after"] = "21000101"

        recent_channel_no_vids_in_range_subscription = channel_subscription_generator(
            preset_dict=recent_channel_preset_dict
        )
        # Run twice, ensure nothing changes between runs
        for _ in range(2):
            transaction_log = recent_channel_no_vids_in_range_subscription.download(dry_run=dry_run)
            assert_transaction_log_matches(
                output_directory=output_directory,
                transaction_log=transaction_log,
                transaction_log_summary_file_name="youtube/test_channel_no_additional_downloads.txt",
            )
            if not dry_run:
                expected_recent_channel_no_vids_in_range_download.assert_files_exist(
                    relative_directory=output_directory
                )

    @pytest.mark.parametrize("dry_run", [True, False])
    def test_rolling_recent_channel_download(
        self,
        channel_subscription_generator,
        recent_channel_preset_dict,
        rolling_recent_channel_preset_dict,
        expected_recent_channel_download,
        expected_rolling_recent_channel_download,
        output_directory,
        dry_run,
    ):
        recent_channel_subscription = channel_subscription_generator(
            preset_dict=recent_channel_preset_dict
        )
        rolling_recent_channel_subscription = channel_subscription_generator(
            preset_dict=rolling_recent_channel_preset_dict
        )

        # First, download recent vids. Always download since we want to test dry-run
        # on the rolling recent portion.
        with assert_debug_log(
            logger=ytdl_sub.downloaders.downloader.download_logger,
            expected_message="RejectedVideoReached, stopping additional downloads",
        ):
            transaction_log = recent_channel_subscription.download()

        expected_recent_channel_download.assert_files_exist(relative_directory=output_directory)
        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_channel_recent.txt",
        )

        # Then, download the rolling recent vids subscription. This should remove one of the
        # two videos
        with assert_debug_log(
            logger=ytdl_sub.downloaders.downloader.download_logger,
            expected_message="ExistingVideoReached, stopping additional downloads",
        ):
            transaction_log = rolling_recent_channel_subscription.download(dry_run=dry_run)

        assert_transaction_log_matches(
            output_directory=output_directory,
            transaction_log=transaction_log,
            transaction_log_summary_file_name="youtube/test_channel_rolling_recent.txt",
            regenerate_transaction_log=True,
        )
        if not dry_run:
            expected_rolling_recent_channel_download.assert_files_exist(
                relative_directory=output_directory
            )

        # Invoke the rolling download again, ensure downloading stopped early from it already
        # existing
        if not dry_run:
            with assert_debug_log(
                logger=ytdl_sub.downloaders.downloader.download_logger,
                expected_message="ExistingVideoReached, stopping additional downloads",
            ):
                transaction_log = rolling_recent_channel_subscription.download()

            assert_transaction_log_matches(
                output_directory=output_directory,
                transaction_log=transaction_log,
                transaction_log_summary_file_name="youtube/test_channel_no_additional_downloads.txt",
            )
            expected_rolling_recent_channel_download.assert_files_exist(
                relative_directory=output_directory
            )
