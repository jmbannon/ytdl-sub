import shlex
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

import pytest

from ytdl_sub.cli.download_args_parser import DownloadArgsParser
from ytdl_sub.cli.main_args_parser import MainArgs
from ytdl_sub.cli.main_args_parser import parser
from ytdl_sub.config.config_validator import ConfigOptions
from ytdl_sub.utils.exceptions import InvalidDlArguments


@pytest.fixture
def config_options_generator() -> Callable:
    def _config_options_generator(dl_aliases: Optional[Dict[str, str]] = None):
        config_options_dict = {
            "working_directory": ".",
        }
        if dl_aliases:
            config_options_dict["dl_aliases"] = dl_aliases

        return ConfigOptions(name="config_options_unit_test", value=config_options_dict)

    return _config_options_generator


@pytest.fixture
def argument_error_msg() -> str:
    return "dl arguments must be in the form of --subscription.option.name 'value'"


def _get_extra_arguments(cmd_string: str) -> List[str]:
    sys_argv = shlex.split(cmd_string)
    _, extra_args = parser.parse_known_args(args=sys_argv)

    return extra_args


class TestDownloadArgsParser:
    @pytest.mark.parametrize(
        "aliases, cmd, expected_sub_dict",
        [
            (
                {"mv": "--preset music_video", "v": "--download.url"},
                "dl --mv --v 123abc",
                {"preset": "music_video", "download": {"url": "123abc"}},
            ),
            (
                {
                    "ch": "--preset yt_channel",
                    "c": "--youtube.channel_url",
                    "name": "--overrides.tv_name",
                    "concert": "--overrides.genre 'Some Genre Name'",
                },
                "dl --ch --c https://youtube.com/channel/123abc --name 'Sweet TV Show' --concert",
                {
                    "preset": "yt_channel",
                    "youtube": {"channel_url": "https://youtube.com/channel/123abc"},
                    "overrides": {"tv_name": "Sweet TV Show", "genre": "Some Genre Name"},
                },
            ),
            (
                None,
                "dl --youtube.playlist_url https://youtube.com/playlist?list=123abc",
                {"youtube": {"playlist_url": "https://youtube.com/playlist?list=123abc"}},
            ),
            (
                None,
                "dl --parameter.using.list[1] 'v1'",
                {"parameter": {"using": {"list": ["v1"]}}},
            ),
            (
                None,
                "dl --parameter.using.list[1] 'v1' --parameter.using.list[2] 'v2'",
                {"parameter": {"using": {"list": ["v1", "v2"]}}},
            ),
            (
                None,
                "dl --parameter.using.list[2] 'v2' --parameter.using.list[1] 'v1'",
                {"parameter": {"using": {"list": ["v1", "v2"]}}},
            ),
            (
                None,
                "dl --parameter.using.list[2] 'v3' --parameter.using.list[1] 'v1' --parameter.using.list[2] 'v2'",
                {"parameter": {"using": {"list": ["v1", "v2"]}}},
            ),
            (
                None,
                "dl --parameter.using.list[3] 'v3' --parameter.using.list[1] 'v1'",
                {"parameter": {"using": {"list": ["v1"]}}},
            ),
            (
                None,
                "dl --parameter.not.using.list[0] 'v0'",
                {"parameter": {"not": {"using": {"list[0]": "v0"}}}},
            ),
        ],
    )
    def test_successful_args(self, config_options_generator, aliases, cmd, expected_sub_dict):
        config_options = config_options_generator(dl_aliases=aliases)
        extra_args = _get_extra_arguments(cmd_string=cmd)

        output_sub_dict = DownloadArgsParser(
            extra_arguments=extra_args, config_options=config_options
        ).to_subscription_dict()

        assert output_sub_dict == expected_sub_dict

    def test_error_uneven_args(self, config_options_generator, argument_error_msg):
        config_options = config_options_generator()
        extra_args = _get_extra_arguments(cmd_string="dl --preset")

        with pytest.raises(InvalidDlArguments, match=argument_error_msg):
            DownloadArgsParser(
                extra_arguments=extra_args, config_options=config_options
            ).to_subscription_dict()

    def test_error_adjacent_values(self, config_options_generator, argument_error_msg):
        config_options = config_options_generator()
        extra_args = _get_extra_arguments(cmd_string="dl --preset buttered toast --test")

        with pytest.raises(InvalidDlArguments, match=argument_error_msg):
            DownloadArgsParser(
                extra_arguments=extra_args, config_options=config_options
            ).to_subscription_dict()

    def test_error_incomplete_list(self, config_options_generator):
        config_options = config_options_generator()
        extra_args = _get_extra_arguments(cmd_string="dl --parameter.using.list[3] 'v3'")

        with pytest.raises(InvalidDlArguments, match="Incomplete list"):
            DownloadArgsParser(
                extra_arguments=extra_args, config_options=config_options
            ).to_subscription_dict()

    def test_error_two_different_types(self, config_options_generator):
        config_options = config_options_generator()
        extra_args = _get_extra_arguments(
            cmd_string="dl --parameter.using.list 'v2' --parameter.using.list[1] 'v1'"
        )

        with pytest.raises(
            InvalidDlArguments,
            match=f"Invalid dl argument --parameter.using.list: "
            "Cannot specify an argument to be two different types",
        ):
            DownloadArgsParser(
                extra_arguments=extra_args, config_options=config_options
            ).to_subscription_dict()

    @pytest.mark.parametrize("main_argument", MainArgs.all())
    def test_error_uses_main_args(self, main_argument, config_options_generator):
        config_options = config_options_generator()
        extra_args = _get_extra_arguments(cmd_string=f"dl {main_argument}")

        with pytest.raises(
            InvalidDlArguments,
            match=f"'{main_argument}' is a ytdl-sub argument and must placed behind 'dl'",
        ):
            DownloadArgsParser(extra_arguments=extra_args, config_options=config_options)
