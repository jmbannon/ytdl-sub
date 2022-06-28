from typing import Dict

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.utils.exceptions import StringFormattingVariableNotFoundException


@pytest.fixture
def config_file() -> ConfigFile:
    return ConfigFile(
        name="config", value={"configuration": {"working_directory": "."}, "presets": {}}
    )


@pytest.fixture
def output_options() -> Dict:
    return {
        "output_directory": "some dir",
        "file_name": "{uid}",
    }


class TestPreset:
    @pytest.mark.parametrize(
        "source, download_strategy",
        [
            ("youtube", {"download_strategy": "video", "video_url": "youtube.com/watch?v=123abc"}),
            (
                "youtube",
                {
                    "download_strategy": "playlist",
                    "playlist_url": "youtube.com/playlist?list=123abc",
                },
            ),
            ("youtube", {"download_strategy": "channel", "channel_url": "youtube.com/c/123abc"}),
            (
                "soundcloud",
                {"download_strategy": "albums_and_singles", "url": "soundcloud.com/123abc"},
            ),
        ],
    )
    def test_bare_minimum_preset(self, config_file, output_options, source, download_strategy):
        _ = Preset(
            config=config_file,
            name="test",
            value={source: download_strategy, "output_options": output_options},
        )

    def test_preset_with_override_variable(self, config_file, output_options):
        _ = Preset(
            config=config_file,
            name="test",
            value={
                "youtube": {
                    "download_strategy": "video",
                    "video_url": "youtube.com/watch?v=123abc",
                },
                "output_options": {"output_directory": "dir", "file_name": "{dne_var}"},
                "overrides": {"dne_var": "not dne"},
            },
        )

    def test_preset_error__source_variable_does_not_exist(self, config_file, output_options):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="Format variable 'dne_var' does not exist",
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "youtube": {
                        "download_strategy": "video",
                        "video_url": "youtube.com/watch?v=123abc",
                    },
                    "output_options": {"output_directory": "dir", "file_name": "{dne_var}"},
                },
            )

    def test_preset_error__override_variable_does_not_exist(self, config_file, output_options):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="Override variable 'dne_var' does not exist",
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "youtube": {
                        "download_strategy": "video",
                        "video_url": "youtube.com/watch?v=123abc",
                    },
                    "output_options": {"output_directory": "{dne_var}", "file_name": "file"},
                },
            )

    def test_preset_error__dict_source_variable_does_not_exist(self, config_file, output_options):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="Format variable 'dne_var' does not exist",
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "youtube": {
                        "download_strategy": "video",
                        "video_url": "youtube.com/watch?v=123abc",
                    },
                    "output_options": {"output_directory": "dir", "file_name": "file"},
                    "nfo_tags": {
                        "nfo_name": "the nfo name",
                        "nfo_root": "the root",
                        "tags": {"tag_a": "{dne_var}"},
                    },
                },
            )

    def test_preset_error__dict_override_variable_does_not_exist(self, config_file, output_options):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="Override variable 'dne_var' does not exist",
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "youtube": {
                        "download_strategy": "video",
                        "video_url": "youtube.com/watch?v=123abc",
                    },
                    "output_options": {"output_directory": "dir", "file_name": "file"},
                    "output_directory_nfo_tags": {
                        "nfo_name": "the nfo name",
                        "nfo_root": "the root",
                        "tags": {"tag_a": "{dne_var}"},
                    },
                },
            )
