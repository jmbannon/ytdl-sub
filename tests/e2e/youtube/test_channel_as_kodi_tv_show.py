from pathlib import Path

import mergedeep
import pytest
from conftest import assert_debug_log
from e2e.expected_download import ExpectedDownloadFile
from e2e.expected_download import ExpectedDownloads

import ytdl_sub.downloaders.downloader
from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.subscriptions.subscription import Subscription


@pytest.fixture
def config_path():
    return "examples/kodi_tv_shows_config.yaml"


@pytest.fixture
def subscription_name():
    return "pz"


@pytest.fixture
def config(config_path):
    return ConfigFile.from_file_path(config_path=config_path)


@pytest.fixture
def subscription_dict(output_directory):
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


####################################################################################################
# FULL CHANNEL FIXTURES


@pytest.fixture
def full_channel_subscription(config, subscription_name, subscription_dict):
    full_channel_preset = Preset.from_dict(
        config=config,
        preset_name=subscription_name,
        preset_dict=subscription_dict,
    )

    return Subscription.from_preset(
        preset=full_channel_preset,
        config=config,
    )


@pytest.fixture
def expected_full_channel_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownloads(
        expected_downloads=[
            # Download mapping
            ExpectedDownloadFile(path=Path(".ytdl-sub-pz-download-archive.json"), md5="b7e7c19d2cf0277e4e42453a64fbaa90"),

            # Output directory files
            ExpectedDownloadFile(path=Path("fanart.jpg"), md5="e6e323373c8902568e96e374817179cf"),
            ExpectedDownloadFile(path=Path("poster.jpg"), md5="a14c593bcc75bb8d2c7145de4767ad01"),
            ExpectedDownloadFile(path=Path("tvshow.nfo"), md5="83c7db96081ac5bdf289fcf396bec157"),

            # Entry files
            ExpectedDownloadFile(path=Path("Season 2010/s2010.e0813 - Oblivion Mod 'Falcor' p.1.jpg"), md5="b58377dfe7c39527e1990a24b36bbd77"),
            ExpectedDownloadFile(path=Path("Season 2010/s2010.e0813 - Oblivion Mod 'Falcor' p.1.mp4"), md5="931a705864c57d21d6fedebed4af6bbc"),
            ExpectedDownloadFile(path=Path("Season 2010/s2010.e0813 - Oblivion Mod 'Falcor' p.1.nfo"), md5="67d8d71d048039080acbba3bce4febaa"),

            ExpectedDownloadFile(path=Path("Season 2010/s2010.e1202 - Oblivion Mod 'Falcor' p.2.jpg"), md5="a5ee6247c8dce255aec79c9a51d49da4"),
            ExpectedDownloadFile(path=Path("Season 2010/s2010.e1202 - Oblivion Mod 'Falcor' p.2.mp4"), md5="d3469b4dca7139cb3dbc38712b6796bf"),
            ExpectedDownloadFile(path=Path("Season 2010/s2010.e1202 - Oblivion Mod 'Falcor' p.2.nfo"), md5="d81f49cedbd7edaee987521e89b37904"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0201 - Jesse's Minecraft Server [Trailer - Feb.1].jpg"), md5="048a19cf0f674437351872c3f312ebf1"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0201 - Jesse's Minecraft Server [Trailer - Feb.1].mp4"), md5="e66287b9832277b6a4d1554e29d9fdcc"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0201 - Jesse's Minecraft Server [Trailer - Feb.1].nfo"), md5="f7c0de89038f8c491bded8a3968720a2"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0227 - Jesse's Minecraft Server [Trailer - Feb.27].jpg"), md5=None),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0227 - Jesse's Minecraft Server [Trailer - Feb.27].mp4"), md5="04ab5cb3cc12325d0c96a7cd04a8b91d"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0227 - Jesse's Minecraft Server [Trailer - Feb.27].nfo"), md5="ee1eda78fa0980bc703e602b5012dd1f"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0321 - Jesse's Minecraft Server [Trailer - Mar.21].jpg"), md5="9baaddc6b62f5b9ae3781eb4eef0e3b3"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0321 - Jesse's Minecraft Server [Trailer - Mar.21].mp4"), md5="025de6099a5c98e6397153c7a62d517d"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0321 - Jesse's Minecraft Server [Trailer - Mar.21].nfo"), md5="61eb6369430da0ab6134d78829a7621b"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0529 - Project Zombie _Official Trailer_ (IP - mc.projectzombie.beastnode.net).jpg"), md5="ce1df7f623fffaefe04606ecbafcfec6"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0529 - Project Zombie _Official Trailer_ (IP - mc.projectzombie.beastnode.net).mp4"), md5="3d9c19835b03355d6fd5d00cd59dbe5b"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0529 - Project Zombie _Official Trailer_ (IP - mc.projectzombie.beastnode.net).nfo"), md5="60f72b99f5c69f9e03a071a12160928f"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0630 - Project Zombie _Fin.jpg"), md5="bc3f511915869720c37617a7de706b2b"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0630 - Project Zombie _Fin.mp4"), md5="4971cb2d4fa29460361031f3fa8e1ea9"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e0630 - Project Zombie _Fin.nfo"), md5="a7b5d9e57d20852f5daf360a1373bb7a"),

            ExpectedDownloadFile(path=Path("Season 2011/s2011.e1121 - Skyrim 'Ultra HD w_Mods' [PC].jpg"), md5="12babdb3b86cd868b90b60d013295f66"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e1121 - Skyrim 'Ultra HD w_Mods' [PC].mp4"), md5="55e9b0add08c48c9c66105da0def2426"),
            ExpectedDownloadFile(path=Path("Season 2011/s2011.e1121 - Skyrim 'Ultra HD w_Mods' [PC].nfo"), md5="fe60e2b6b564f9316b6c7c183e1cf300"),

            ExpectedDownloadFile(path=Path("Season 2012/s2012.e0123 - Project Zombie _Map Trailer.jpg"), md5="82d303e16aba75acdde30b15c4154231"),
            ExpectedDownloadFile(path=Path("Season 2012/s2012.e0123 - Project Zombie _Map Trailer.mp4"), md5="65e4ce53ed5ec4139995469f99477a50"),
            ExpectedDownloadFile(path=Path("Season 2012/s2012.e0123 - Project Zombie _Map Trailer.nfo"), md5="c8900adcca83c473c79a4afbc7ad2de1"),

            ExpectedDownloadFile(path=Path("Season 2013/s2013.e0719 - Project Zombie Rewind _Trailer.jpg"), md5="83b1af4c3614d262b2ad419586fff730"),
            ExpectedDownloadFile(path=Path("Season 2013/s2013.e0719 - Project Zombie Rewind _Trailer.mp4"), md5="18620a8257a686beda65e54add4d4cd1"),
            ExpectedDownloadFile(path=Path("Season 2013/s2013.e0719 - Project Zombie Rewind _Trailer.nfo"), md5="1c993c41d4308a6049333154d0adee16"),

            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.jpg"), md5="2a24de903059f48c7d0df0476046c975"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.mp4"), md5="82f6ee7253e1dbb83ae7215af08ffacc"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.nfo"), md5="cc7886aae3af6b7b0facd82f95390242"),

            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.jpg"), md5="c8baea83b9edeb081657f1130a1031f7"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.mp4"), md5="e733b4cc385b953b08c8eb0f47e03c1e"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.nfo"), md5="2b3ccb3f1ef81ee49fe1afb88f275a09"),
        ]
    )
    # fmt: on


####################################################################################################
# RECENT CHANNEL FIXTURES
@pytest.fixture
def recent_channel_subscription_dict(subscription_dict):
    # TODO: remove this hack by using a different channel
    del subscription_dict["ytdl_options"]["break_on_reject"]
    return mergedeep.merge(
        subscription_dict,
        {
            "preset": "yt_channel_as_tv__recent",
            "youtube": {"after": "20150101"},
        },
    )


@pytest.fixture
def recent_channel_subscription(config, subscription_name, recent_channel_subscription_dict):
    recent_channel_preset = Preset.from_dict(
        config=config,
        preset_name=subscription_name,
        preset_dict=recent_channel_subscription_dict,
    )

    return Subscription.from_preset(
        preset=recent_channel_preset,
        config=config,
    )


@pytest.fixture
def expected_recent_channel_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownloads(
        expected_downloads=[
            # Download mapping
            ExpectedDownloadFile(path=Path(".ytdl-sub-pz-download-archive.json"), md5="b1675ca4d9f0d4b9c2102b6749e4cdfd"),

            # Output directory files
            ExpectedDownloadFile(path=Path("fanart.jpg"), md5="e6e323373c8902568e96e374817179cf"),
            ExpectedDownloadFile(path=Path("poster.jpg"), md5="a14c593bcc75bb8d2c7145de4767ad01"),
            ExpectedDownloadFile(path=Path("tvshow.nfo"), md5="83c7db96081ac5bdf289fcf396bec157"),

            # Recent Entry files
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.jpg"), md5="2a24de903059f48c7d0df0476046c975"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.mp4"), md5="82f6ee7253e1dbb83ae7215af08ffacc"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.nfo"), md5="cc7886aae3af6b7b0facd82f95390242"),

            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.jpg"), md5="c8baea83b9edeb081657f1130a1031f7"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.mp4"), md5="e733b4cc385b953b08c8eb0f47e03c1e"),
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.nfo"), md5="2b3ccb3f1ef81ee49fe1afb88f275a09"),
        ]
    )
    # fmt: on


####################################################################################################
# RECENT CHANNEL FIXTURES -- NO VIDS IN RANGE
@pytest.fixture
def recent_channel_no_vids_in_range_subscription_dict(subscription_dict):
    # TODO: remove this hack by using a different channel
    del subscription_dict["ytdl_options"]["break_on_reject"]
    return mergedeep.merge(
        subscription_dict,
        {
            "preset": "yt_channel_as_tv__recent",
            "youtube": {"after": "20880101"},
        },
    )


@pytest.fixture
def recent_channel_no_vids_in_range_subscription(
    config, subscription_name, recent_channel_no_vids_in_range_subscription_dict
):
    recent_channel_preset = Preset.from_dict(
        config=config,
        preset_name=subscription_name,
        preset_dict=recent_channel_no_vids_in_range_subscription_dict,
    )

    return Subscription.from_preset(
        preset=recent_channel_preset,
        config=config,
    )


@pytest.fixture
def expected_recent_channel_no_vids_in_range_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownloads(
        expected_downloads=[
            # Download mapping
            ExpectedDownloadFile(path=Path(".ytdl-sub-pz-download-archive.json"), md5="99914b932bd37a50b983c5e7c90ae93b"),

            # Output directory files
            ExpectedDownloadFile(path=Path("fanart.jpg"), md5="e6e323373c8902568e96e374817179cf"),
            ExpectedDownloadFile(path=Path("poster.jpg"), md5="a14c593bcc75bb8d2c7145de4767ad01"),
            ExpectedDownloadFile(path=Path("tvshow.nfo"), md5="83c7db96081ac5bdf289fcf396bec157"),
        ]
    )
    # fmt: on


####################################################################################################
# ROLLING RECENT CHANNEL FIXTURES
@pytest.fixture
def rolling_recent_channel_subscription_dict(recent_channel_subscription_dict):
    return mergedeep.merge(
        recent_channel_subscription_dict,
        {
            "preset": "yt_channel_as_tv__only_recent",
            "output_options": {"keep_files_after": "20181101"},
        },
    )


@pytest.fixture
def rolling_recent_channel_subscription(
    config, subscription_name, rolling_recent_channel_subscription_dict
):
    rolling_recent_channel_preset = Preset.from_dict(
        config=config,
        preset_name=subscription_name,
        preset_dict=rolling_recent_channel_subscription_dict,
    )

    return Subscription.from_preset(
        preset=rolling_recent_channel_preset,
        config=config,
    )


@pytest.fixture
def expected_rolling_recent_channel_download():
    # turn off black formatter here for readability
    # fmt: off
    return ExpectedDownloads(
        expected_downloads=[
            # Download mapping
            ExpectedDownloadFile(path=Path(".ytdl-sub-pz-download-archive.json"), md5="9ae3463bd2dc39830003aba68a276df4"),

            # Output directory files
            ExpectedDownloadFile(path=Path("fanart.jpg"), md5="e6e323373c8902568e96e374817179cf"),
            ExpectedDownloadFile(path=Path("poster.jpg"), md5="a14c593bcc75bb8d2c7145de4767ad01"),
            ExpectedDownloadFile(path=Path("tvshow.nfo"), md5="83c7db96081ac5bdf289fcf396bec157"),

            # Rolling Recent Entry files
            ExpectedDownloadFile(path=Path("Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.jpg"), md5="c8baea83b9edeb081657f1130a1031f7"),
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

    def test_full_channel_download(
        self, full_channel_subscription, expected_full_channel_download, output_directory
    ):
        full_channel_subscription.download()
        expected_full_channel_download.assert_files_exist(relative_directory=output_directory)

    def test_full_channel_dry_run(
        self, full_channel_subscription, expected_full_channel_download, output_directory
    ):
        transaction_log = full_channel_subscription.download(dry_run=True)
        expected_full_channel_download.assert_dry_run_files_logged(transaction_log=transaction_log)

    def test_recent_channel_download(
        self, recent_channel_subscription, expected_recent_channel_download, output_directory
    ):
        recent_channel_subscription.download()
        expected_recent_channel_download.assert_files_exist(relative_directory=output_directory)

        # try downloading again, ensure nothing more was downloaded
        with assert_debug_log(
            logger=ytdl_sub.downloaders.downloader.logger,
            expected_message="ExistingVideoReached, stopping additional downloads",
        ):
            recent_channel_subscription.download()
            expected_recent_channel_download.assert_files_exist(relative_directory=output_directory)

    def test_recent_channel_dry_run(
        self, recent_channel_subscription, expected_recent_channel_download, output_directory
    ):
        transaction_log = recent_channel_subscription.download(dry_run=True)
        expected_recent_channel_download.assert_dry_run_files_logged(
            transaction_log=transaction_log
        )

    def test_recent_channel_download__no_vids_in_range(
        self,
        recent_channel_no_vids_in_range_subscription,
        expected_recent_channel_no_vids_in_range_download,
        output_directory,
    ):
        recent_channel_no_vids_in_range_subscription.download()
        expected_recent_channel_no_vids_in_range_download.assert_files_exist(
            relative_directory=output_directory
        )

        # Try again, make sure its the same
        recent_channel_no_vids_in_range_subscription.download()
        expected_recent_channel_no_vids_in_range_download.assert_files_exist(
            relative_directory=output_directory
        )

    def test_recent_channel_dry_run__no_vids_in_range(
        self,
        recent_channel_no_vids_in_range_subscription,
        expected_recent_channel_no_vids_in_range_download,
        output_directory,
    ):
        transaction_log = recent_channel_no_vids_in_range_subscription.download(dry_run=True)
        expected_recent_channel_no_vids_in_range_download.assert_dry_run_files_logged(
            transaction_log=transaction_log
        )

    def test_rolling_recent_channel_download(
        self,
        recent_channel_subscription,
        rolling_recent_channel_subscription,
        expected_recent_channel_download,
        expected_rolling_recent_channel_download,
        output_directory,
    ):
        # First, download recent vids
        with assert_debug_log(
            logger=ytdl_sub.downloaders.downloader.logger,
            expected_message="RejectedVideoReached, stopping additional downloads",
        ):
            recent_channel_subscription.download()
            expected_recent_channel_download.assert_files_exist(relative_directory=output_directory)

        # Then, download the rolling recent vids subscription. This should remove one of the
        # two videos
        with assert_debug_log(
            logger=ytdl_sub.downloaders.downloader.logger,
            expected_message="ExistingVideoReached, stopping additional downloads",
        ):
            rolling_recent_channel_subscription.download()
            expected_rolling_recent_channel_download.assert_files_exist(
                relative_directory=output_directory
            )

        # Invoke the rolling download again, ensure downloading stopped early from it already
        # existing
        with assert_debug_log(
            logger=ytdl_sub.downloaders.downloader.logger,
            expected_message="ExistingVideoReached, stopping additional downloads",
        ):
            rolling_recent_channel_subscription.download()
            expected_rolling_recent_channel_download.assert_files_exist(
                relative_directory=output_directory
            )
