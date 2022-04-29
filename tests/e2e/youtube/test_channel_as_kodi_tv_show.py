import tempfile
from pathlib import Path

import pytest
from config.config_file import ConfigFile
from config.subscription import SubscriptionValidator
from e2e.expected_download import ExpectedDownload


@pytest.fixture()
def output_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


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
def subscription_dict(output_directory, subscription_name):
    return {
        "preset": "yt_channel_as_tv",
        "youtube": {"channel_id": "UCcRSMoQqXc_JrBZRHDFGbqA"},
        # override the output directory with our fixture-generated dir
        "output_options": {"output_directory": str(Path(output_directory) / subscription_name)},
        # download the worst format so it is fast
        "ytdl_options": {
            "format": "worst[ext=mp4]",
            "max_views": 100000,  # do not download the popular PJ concert
        },
        "overrides": {"tv_show_name": "Project / Zombie"},
    }


@pytest.fixture
def full_channel_subscription(config, subscription_name, subscription_dict):
    return SubscriptionValidator.from_dict(
        config=config,
        subscription_name=subscription_name,
        subscription_dict=subscription_dict,
    ).to_subscription()


@pytest.fixture
def expected_full_channel_download():
    # turn of black formatter here for readability
    # fmt: off
    return ExpectedDownload(
        expected_md5_file_hashes={
            # Download mapping
            Path("pz/.ytdl-subscribe-pz-download-mapping.json"): "add71021318bf87a3facb965fd38bd7f",

            # Output directory files
            Path("pz/fanart.jpg"): "e6e323373c8902568e96e374817179cf",
            Path("pz/poster.jpg"): "a14c593bcc75bb8d2c7145de4767ad01",
            Path("pz/tvshow.nfo"): "83c7db96081ac5bdf289fcf396bec157",

            # Entry files
            Path("pz/Season 2010/s2010.e0813 - Oblivion Mod 'Falcor' p.1.jpg"): "b58377dfe7c39527e1990a24b36bbd77",
            Path("pz/Season 2010/s2010.e0813 - Oblivion Mod 'Falcor' p.1.mp4"): "931a705864c57d21d6fedebed4af6bbc",
            Path("pz/Season 2010/s2010.e0813 - Oblivion Mod 'Falcor' p.1.nfo"): "67d8d71d048039080acbba3bce4febaa",

            Path("pz/Season 2010/s2010.e1202 - Oblivion Mod 'Falcor' p.2.jpg"): "a5ee6247c8dce255aec79c9a51d49da4",
            Path("pz/Season 2010/s2010.e1202 - Oblivion Mod 'Falcor' p.2.mp4"): "d3469b4dca7139cb3dbc38712b6796bf",
            Path("pz/Season 2010/s2010.e1202 - Oblivion Mod 'Falcor' p.2.nfo"): "d81f49cedbd7edaee987521e89b37904",

            Path("pz/Season 2011/s2011.e0201 - Jesse's Minecraft Server [Trailer - Feb.1].jpg"): "048a19cf0f674437351872c3f312ebf1",
            Path("pz/Season 2011/s2011.e0201 - Jesse's Minecraft Server [Trailer - Feb.1].mp4"): "e66287b9832277b6a4d1554e29d9fdcc",
            Path("pz/Season 2011/s2011.e0201 - Jesse's Minecraft Server [Trailer - Feb.1].nfo"): "f7c0de89038f8c491bded8a3968720a2",

            Path("pz/Season 2011/s2011.e0227 - Jesse's Minecraft Server [Trailer - Feb.27].jpg"): "2e58e4d5f06ce5d1c3336fa493470135",
            Path("pz/Season 2011/s2011.e0227 - Jesse's Minecraft Server [Trailer - Feb.27].mp4"): "04ab5cb3cc12325d0c96a7cd04a8b91d",
            Path("pz/Season 2011/s2011.e0227 - Jesse's Minecraft Server [Trailer - Feb.27].nfo"): "ee1eda78fa0980bc703e602b5012dd1f",

            Path("pz/Season 2011/s2011.e0321 - Jesse's Minecraft Server [Trailer - Mar.21].jpg"): "9baaddc6b62f5b9ae3781eb4eef0e3b3",
            Path("pz/Season 2011/s2011.e0321 - Jesse's Minecraft Server [Trailer - Mar.21].mp4"): "025de6099a5c98e6397153c7a62d517d",
            Path("pz/Season 2011/s2011.e0321 - Jesse's Minecraft Server [Trailer - Mar.21].nfo"): "61eb6369430da0ab6134d78829a7621b",

            Path("pz/Season 2011/s2011.e0529 - Project Zombie _Official Trailer_ (IP - mc.projectzombie.beastnode.net).jpg"): "ce1df7f623fffaefe04606ecbafcfec6",
            Path("pz/Season 2011/s2011.e0529 - Project Zombie _Official Trailer_ (IP - mc.projectzombie.beastnode.net).mp4"): "3d9c19835b03355d6fd5d00cd59dbe5b",
            Path("pz/Season 2011/s2011.e0529 - Project Zombie _Official Trailer_ (IP - mc.projectzombie.beastnode.net).nfo"): "60f72b99f5c69f9e03a071a12160928f",

            Path("pz/Season 2011/s2011.e0630 - Project Zombie _Fin.jpg"): "bc3f511915869720c37617a7de706b2b",
            Path("pz/Season 2011/s2011.e0630 - Project Zombie _Fin.mp4"): "4971cb2d4fa29460361031f3fa8e1ea9",
            Path("pz/Season 2011/s2011.e0630 - Project Zombie _Fin.nfo"): "a7b5d9e57d20852f5daf360a1373bb7a",

            Path("pz/Season 2011/s2011.e1121 - Skyrim 'Ultra HD w_Mods' [PC].jpg"): "12babdb3b86cd868b90b60d013295f66",
            Path("pz/Season 2011/s2011.e1121 - Skyrim 'Ultra HD w_Mods' [PC].mp4"): "55e9b0add08c48c9c66105da0def2426",
            Path("pz/Season 2011/s2011.e1121 - Skyrim 'Ultra HD w_Mods' [PC].nfo"): "fe60e2b6b564f9316b6c7c183e1cf300",

            Path("pz/Season 2012/s2012.e0123 - Project Zombie _Map Trailer.jpg"): "82d303e16aba75acdde30b15c4154231",
            Path("pz/Season 2012/s2012.e0123 - Project Zombie _Map Trailer.mp4"): "65e4ce53ed5ec4139995469f99477a50",
            Path("pz/Season 2012/s2012.e0123 - Project Zombie _Map Trailer.nfo"): "c8900adcca83c473c79a4afbc7ad2de1",

            Path("pz/Season 2013/s2013.e0719 - Project Zombie Rewind _Trailer.jpg"): "83b1af4c3614d262b2ad419586fff730",
            Path("pz/Season 2013/s2013.e0719 - Project Zombie Rewind _Trailer.mp4"): "18620a8257a686beda65e54add4d4cd1",
            Path("pz/Season 2013/s2013.e0719 - Project Zombie Rewind _Trailer.nfo"): "1c993c41d4308a6049333154d0adee16",

            Path("pz/Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.jpg"): "2a24de903059f48c7d0df0476046c975",
            Path("pz/Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.mp4"): "82f6ee7253e1dbb83ae7215af08ffacc",
            Path("pz/Season 2018/s2018.e1029 - Jesse's Minecraft Server _ Teaser Trailer.nfo"): "cc7886aae3af6b7b0facd82f95390242",

            Path("pz/Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.jpg"): "c8baea83b9edeb081657f1130a1031f7",
            Path("pz/Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.mp4"): "e733b4cc385b953b08c8eb0f47e03c1e",
            Path("pz/Season 2018/s2018.e1102 - Jesse's Minecraft Server _ IP mc.jesse.id.nfo"): "2b3ccb3f1ef81ee49fe1afb88f275a09",
        }
    )
    # fmt: on


class TestChannelAsKodiTvShow:
    def test_full_channel_download(self, full_channel_subscription, expected_full_channel_download, output_directory):
        full_channel_subscription.download()
        expected_full_channel_download.assert_files_exist(relative_directory=output_directory)
