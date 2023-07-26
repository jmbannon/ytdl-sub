import re

import pytest

from ytdl_sub.config.preset import Preset
from ytdl_sub.plugins.nfo_tags import NfoTagsOptions
from ytdl_sub.utils.exceptions import StringFormattingVariableNotFoundException
from ytdl_sub.utils.exceptions import ValidationException


class TestPreset:
    @pytest.mark.parametrize(
        "download_value",
        [
            {"url": "youtube.com/watch?v=123abc"},
            {"urls": [{"url": "youtube.com/watch?v=123abc"}]},
            ###########################################################
            ##### OLD download_strategy format
            {"download_strategy": "url", "url": "youtube.com/watch?v=123abc"},
            {"download_strategy": "multi-url", "urls": [{"url": "youtube.com/watch?v=123abc"}]},
        ],
    )
    def test_bare_minimum_preset(self, config_file, output_options, download_value):
        _ = Preset(
            config=config_file,
            name="test",
            value={"download": download_value, "output_options": output_options},
        )

    def test_preset_with_override_variable(self, config_file, output_options, youtube_video):
        _ = Preset(
            config=config_file,
            name="test",
            value={
                "download": youtube_video,
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
                "download": youtube_video,
                "output_options": output_options,
                "nfo_tags": {"tags": {"key-2": "this-preset"}},
            },
        )

        nfo_options: NfoTagsOptions = preset.plugins.get(NfoTagsOptions)
        tags_string_dict = {
            key: formatter[0].format_string
            for key, formatter in nfo_options.tags.string_tags.items()
        }

        assert tags_string_dict == {"key-1": "preset_0", "key-2": "this-preset"}

    @pytest.mark.parametrize(
        "preset_value", [["parent_preset_1", "parent_preset_2"], "parent_preset_3"]
    )
    def test_preset_multiple_parents(
        self, config_file, output_options, youtube_video, preset_value
    ):
        preset = Preset(
            config=config_file,
            name="test",
            value={
                "preset": preset_value,
                "download": youtube_video,
                "output_options": output_options,
                "nfo_tags": {"tags": {"key-3": "this-preset"}},
            },
        )

        nfo_options: NfoTagsOptions = preset.plugins.get(NfoTagsOptions)
        tags_string_dict = {
            key: formatter[0].format_string
            for key, formatter in nfo_options.tags.string_tags.items()
        }

        assert tags_string_dict == {
            "key-1": "preset_0",
            "key-2": "preset_2",
            "key-3": "this-preset",
        }

    def test_preset_datetime_with_override(self, config_file, youtube_video, output_options):
        preset = Preset(
            config=config_file,
            name="test",
            value={
                "download": youtube_video,
                "output_options": dict(
                    output_options,
                    **{"maintain_download_archive": True, "keep_files_after": "today-{ttl}"},
                ),
                "overrides": {"ttl": "2months"},
            },
        )
        assert (
            preset.overrides.apply_formatter(formatter=preset.output_options.keep_files_after)
            == "today-2months"
        )

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
                    "download": youtube_video,
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
                    "download": youtube_video,
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
                    "download": youtube_video,
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
                    "download": youtube_video,
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
            match="Format variable 'dne_var' does not exist",
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "download": youtube_video,
                    "output_options": output_options,
                    "output_directory_nfo_tags": {
                        "nfo_name": "the nfo name",
                        "nfo_root": "the root",
                        "tags": {"tag_a": "{dne_var}"},
                    },
                },
            )

    def test_preset_with_multi_url__contains_empty_url(self, config_file, output_options):
        _ = Preset(
            config=config_file,
            name="test",
            value={
                "download": {
                    "urls": [{"url": "non-empty url"}, {"url": ""}],  # empty url
                },
                "output_options": output_options,
            },
        )

    def test_preset_with_multi_url__contains_all_empty_urls_errors(
        self, config_file, output_options
    ):
        with pytest.raises(
            ValidationException,
            match=re.escape(
                "Validation error in test.download: Must contain at least one "
                "url that is non-empty"
            ),
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "download": {
                        "urls": [{"url": "{url}"}, {"url": "{url2}"}],
                    },
                    "output_options": output_options,
                    "overrides": {"url": "", "url2": ""},
                },
            )
