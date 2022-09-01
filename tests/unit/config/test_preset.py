from typing import Dict

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import Preset
from ytdl_sub.plugins.nfo_tags import NfoTagsOptions
from ytdl_sub.utils.exceptions import StringFormattingVariableNotFoundException
from ytdl_sub.utils.exceptions import ValidationException


@pytest.fixture
def config_file() -> ConfigFile:
    return ConfigFile(
        name="config",
        value={
            "configuration": {"working_directory": "."},
            "presets": {
                "parent_preset_0": {"nfo_tags": {"tags": {"key-1": "preset_0"}}},
                "parent_preset_1": {
                    "preset": "parent_preset_0",
                    "nfo_tags": {
                        "nfo_name": "{uid}.nfo",
                        "nfo_root": "root",
                        "tags": {"key-2": "preset_1"},
                    },
                },
                "parent_preset_2": {
                    "nfo_tags": {
                        "nfo_name": "{uid}.nfo",
                        "nfo_root": "root",
                        "tags": {"key-2": "preset_2", "key-3": "preset_2"},
                    }
                },
                "preset_self_loop": {"preset": "preset_self_loop"},
                "preset_loop_0": {"preset": "preset_loop_1"},
                "preset_loop_1": {"preset": "preset_loop_0"},
            },
        },
    )


@pytest.fixture
def output_options() -> Dict:
    return {
        "output_directory": "some dir",
        "file_name": "{uid}",
    }


@pytest.fixture
def youtube_video() -> Dict:
    return {
        "download_strategy": "video",
        "video_url": "youtube.com/watch?v=123abc",
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

    def test_preset_with_override_variable(self, config_file, output_options, youtube_video):
        _ = Preset(
            config=config_file,
            name="test",
            value={
                "youtube": youtube_video,
                "output_options": {"output_directory": "dir", "file_name": "{dne_var}"},
                "overrides": {"dne_var": "not dne"},
            },
        )

    def test_preset_parent(self, config_file, output_options, youtube_video):
        preset = Preset(
            config=config_file,
            name="test",
            value={
                "preset": "parent_preset_1",
                "youtube": youtube_video,
                "output_options": output_options,
                "nfo_tags": {"tags": {"key-2": "this-preset"}},
            },
        )

        nfo_options: NfoTagsOptions = preset.plugins.get(NfoTagsOptions)
        tags_string_dict = {
            key: formatter.format_string for key, formatter in nfo_options.tags.string_tags.items()
        }

        assert tags_string_dict == {"key-1": "preset_0", "key-2": "this-preset"}

    def test_preset_multiple_parents(self, config_file, output_options, youtube_video):
        preset = Preset(
            config=config_file,
            name="test",
            value={
                "preset": ["parent_preset_1", "parent_preset_2"],
                "youtube": youtube_video,
                "output_options": output_options,
                "nfo_tags": {"tags": {"key-3": "this-preset"}},
            },
        )

        nfo_options: NfoTagsOptions = preset.plugins.get(NfoTagsOptions)
        tags_string_dict = {
            key: formatter.format_string for key, formatter in nfo_options.tags.string_tags.items()
        }

        assert tags_string_dict == {
            "key-1": "preset_0",
            "key-2": "preset_1",
            "key-3": "this-preset",
        }

    @pytest.mark.parametrize(
        "parent_preset", ["preset_self_loop", "preset_loop_0", "preset_loop_1"]
    )
    def test_preset_error__parent_loop(
        self, config_file, output_options, youtube_video, parent_preset
    ):
        with pytest.raises(ValidationException, match="preset loop detected"):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "preset": parent_preset,
                    "youtube": youtube_video,
                    "output_options": output_options,
                },
            )

    def test_preset_error__source_variable_does_not_exist(
        self, config_file, output_options, youtube_video
    ):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="Format variable 'dne_var' does not exist",
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "youtube": youtube_video,
                    "output_options": {"output_directory": "dir", "file_name": "{dne_var}"},
                },
            )

    def test_preset_error__override_variable_does_not_exist(
        self, config_file, output_options, youtube_video
    ):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="Override variable 'dne_var' does not exist",
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "youtube": youtube_video,
                    "output_options": {"output_directory": "{dne_var}", "file_name": "file"},
                },
            )

    def test_preset_error__dict_source_variable_does_not_exist(
        self, config_file, output_options, youtube_video
    ):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="Format variable 'dne_var' does not exist",
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "youtube": youtube_video,
                    "output_options": {"output_directory": "dir", "file_name": "file"},
                    "nfo_tags": {
                        "nfo_name": "the nfo name",
                        "nfo_root": "the root",
                        "tags": {"tag_a": "{dne_var}"},
                    },
                },
            )

    def test_preset_error__dict_override_variable_does_not_exist(
        self, config_file, output_options, youtube_video
    ):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="Override variable 'dne_var' does not exist",
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "youtube": youtube_video,
                    "output_options": {"output_directory": "dir", "file_name": "file"},
                    "output_directory_nfo_tags": {
                        "nfo_name": "the nfo name",
                        "nfo_root": "the root",
                        "tags": {"tag_a": "{dne_var}"},
                    },
                },
            )
