import shlex
from typing import Callable
from typing import Dict
from typing import Optional

import pytest

from ytdl_sub.cli.download_args_parser import DownloadArgsParser
from ytdl_sub.cli.main_args_parser import parser
from ytdl_sub.config.config_file import ConfigOptions


@pytest.fixture
def config_options_generator() -> Callable:
    def _config_options_generator(dl_aliases: Optional[Dict[str, str]]):
        config_options_dict = {
            "working_directory": ".",
        }
        if dl_aliases:
            config_options_dict["dl_aliases"] = dl_aliases

        return ConfigOptions(name="config_options_unit_test", value=config_options_dict)

    return _config_options_generator


class TestDownloadArgsParser:
    @pytest.mark.parametrize(
        "aliases, cmd, expected_sub_dict",
        [
            (
                {"mv": "--preset yt_music_video", "v": "--youtube.video_id"},
                "dl --mv --v 123abc",
                {"preset": "yt_music_video", "youtube": {"video_id": "123abc"}},
            ),
            (
                {
                    "ch": "--preset yt_channel",
                    "c": "--youtube.channel_id",
                    "name": "--overrides.tv_name",
                    "concert": "--overrides.genre 'Some Genre Name'",
                },
                "dl --ch --c 123abc --name 'Sweet TV Show' --concert",
                {
                    "preset": "yt_channel",
                    "youtube": {"channel_id": "123abc"},
                    "overrides": {"tv_name": "Sweet TV Show", "genre": "Some Genre Name"},
                },
            ),
            (None, "dl --youtube.playlist_id 123abc", {"youtube": {"playlist_id": "123abc"}}),
        ],
    )
    def test_successful_args(self, config_options_generator, aliases, cmd, expected_sub_dict):
        config_options = config_options_generator(dl_aliases=aliases)
        sys_argv = shlex.split(cmd)

        args, extra_args = parser.parse_known_args(args=sys_argv)

        output_sub_dict = DownloadArgsParser(
            extra_arguments=extra_args, config_options=config_options
        ).to_subscription_dict()

        assert output_sub_dict == expected_sub_dict
