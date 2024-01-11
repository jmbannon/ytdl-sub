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
            {"url": "youtube.com/watch?v=123abc"},  # url download strategy
            {"urls": [{"url": "youtube.com/watch?v=123abc"}]},  # multi-url download strategy
            "youtube.com/watch?v=123abc",  # single string
            ["youtube.com/watch?v=123abc", "youtube.com/watch?v=123xyz"],  # list of strings
            [{"url": "youtube.com/watch?v=123abc"}, "youtube.com/watch?v=123abc"],  # dict and str
            # OLD download_strategy format
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
            match="contains the following variables that do not exist: dne_var",
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
            match="contains the following variables that do not exist: dne_var",
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
            match="contains the following variables that do not exist: dne_var",
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
            match="contains the following variables that do not exist: dne_var",
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

    def test_preset_error__dict_override_variable_not_static(
        self, config_file, output_options, youtube_video
    ):
        with pytest.raises(
            StringFormattingVariableNotFoundException,
            match="static formatters must contain variables that "
            "have no dependency to entry variables",
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "download": youtube_video,
                    "output_options": {
                        "output_directory": "{title}",
                        "file_name": "{uid}",
                    },
                },
            )

    def test_preset_with_multi_url__contains_empty_url(self, config_file, output_options):
        _ = Preset(
            config=config_file,
            name="test",
            value={
                "download": [{"url": "non-empty url"}, {"url": ""}],  # empty url
                "output_options": output_options,
            },
        )

    @pytest.mark.parametrize(
        "entry_variable_name",
        [
            "title",
            "playlist_uid",
            "source_title",
            "playlist_max_upload_year",
        ],
    )
    def test_preset_error_override_variable_collides_with_entry_variable(
        self, config_file, output_options, youtube_video, entry_variable_name: str
    ):
        with pytest.raises(
            ValidationException,
            match=re.escape(
                f"Override variable with name {entry_variable_name} cannot be used since"
                " it is a built-in ytdl-sub entry variable name."
            ),
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "download": youtube_video,
                    "output_options": {"output_directory": "dir", "file_name": "{dne_var}"},
                    "overrides": {entry_variable_name: "fail"},
                },
            )

    def test_preset_error_override_variable_collides_added_variable(
        self, config_file, output_options, youtube_video
    ):
        with pytest.raises(
            ValidationException,
            match=re.escape(
                f"Override variable with name subtitles_ext cannot be used since"
                " it is added by a plugin."
            ),
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "download": youtube_video,
                    "output_options": {"output_directory": "dir", "file_name": "ack"},
                    "subtitles": {
                        "embed_subtitles": True,
                    },
                    "overrides": {"subtitles_ext": "collide"},
                },
            )

    @pytest.mark.parametrize(
        "function_name",
        [
            "%extract_field_from_siblings",
            "%sanitize",
            "%array",
        ],
    )
    def test_preset_error_override_variable_collides_with_custom_function(
        self, config_file, output_options, youtube_video, function_name: str
    ):
        with pytest.raises(
            ValidationException,
            match=re.escape(
                f"Override function definition with name {function_name} cannot be used since"
                " it is a built-in ytdl-sub function name."
            ),
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "download": youtube_video,
                    "output_options": {"output_directory": "dir", "file_name": "{dne_var}"},
                    "overrides": {function_name: "fail"},
                },
            )

    def test_preset_error_override_added_variable_collides_with_built_in(
        self, config_file, output_options
    ):
        with pytest.raises(
            ValidationException,
            match=re.escape(
                "Cannot use the variable name title because it exists as a "
                "built-in ytdl-sub variable name."
            ),
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "download": {
                        "url": "youtube.com/watch?v=123abc",
                        "variables": {"title": "nope"},
                    },
                    "output_options": {"output_directory": "dir", "file_name": "acjk"},
                },
            )

    def test_preset_error_override_added_variable_collides_with_override(
        self, config_file, output_options
    ):
        with pytest.raises(
            ValidationException,
            match=re.escape(
                "Override variable with name the_bad_one cannot be used since "
                "it is added by a plugin."
            ),
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "download": {
                        "url": "youtube.com/watch?v=123abc",
                        "variables": {"the_bad_one": "should error"},
                    },
                    "output_options": {"output_directory": "dir", "file_name": "acjk"},
                    "overrides": {"the_bad_one": "ack"},
                },
            )

    @pytest.mark.parametrize(
        "name", ["!ack", "*asfsaf", "1234352", "--234asdf", "___asdf", "1asdfasdfasd"]
    )
    @pytest.mark.parametrize("is_function", [True, False])
    def test_preset_error_overrides_invalid_variable_name(
        self, config_file, youtube_video, output_options, name: str, is_function: bool
    ):
        name_type = "function" if is_function else "variable"
        name = f"%{name}" if is_function else name

        with pytest.raises(
            ValidationException,
            match=re.escape(
                f"Override {name_type} with name {name} is invalid."
                " Names must be lower_snake_cased and begin with a letter."
            ),
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "download": youtube_video,
                    "output_options": output_options,
                    "overrides": {name: "ack"},
                },
            )

    def test_preset_error_added_url_variable_cannot_resolve(self, config_file, output_options):
        with pytest.raises(
            ValidationException,
            match=re.escape(
                "variable the_bad_one cannot use the variables subtitles_ext because it "
                "depends on other variables that are computed later in execution"
            ),
        ):
            _ = Preset(
                config=config_file,
                name="test",
                value={
                    "download": {
                        "url": "youtube.com/watch?v=123abc",
                        "variables": {"the_bad_one": "{subtitles_ext}"},
                    },
                    "subtitles": {
                        "embed_subtitles": True,
                    },
                    "output_options": {"output_directory": "dir", "file_name": "acjk"},
                },
            )
