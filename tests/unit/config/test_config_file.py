import os.path
import re
from pathlib import Path
from typing import Dict
from typing import Optional

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.plugin.plugin_mapping import PluginMapping
from ytdl_sub.config.preset import PRESET_KEYS
from ytdl_sub.utils.exceptions import ValidationException


class TestConfigFilePartiallyValidatesPresets:
    @classmethod
    def _partial_validate(
        cls, preset_dict: Dict, expected_error_message: Optional[str] = None
    ) -> None:
        def _config_create() -> None:
            _ = ConfigFile(
                name="test_partial_validate",
                value={
                    "configuration": {"working_directory": "."},
                    "presets": {"partial_preset": preset_dict},
                },
            )

        if expected_error_message:
            with pytest.raises(ValidationException, match=re.escape(expected_error_message)):
                _config_create()
        else:
            _config_create()

    @pytest.mark.parametrize(
        "preset_dict",
        [
            {"nfo_tags": {"tags": {"key-1": "preset_0"}}},
            {"output_directory_nfo_tags": {"nfo_root": "test"}},
            {"output_options": {"file_name": "test"}},
            {"output_options": {"keep_files_after": "today"}},
            {"ytdl_options": {"format": "best"}},
            {"format": "best"},
            {"overrides": {"a": "b"}},
        ],
    )
    def test_success(self, preset_dict: Dict):
        self._partial_validate(preset_dict)

    @pytest.mark.parametrize("key", ["output_options", "overrides", "ytdl_options"])
    def test_success__empty_preset_keys(self, key):
        self._partial_validate({key: {}})

    @pytest.mark.parametrize("plugin", PluginMapping.plugins())
    def test_success__empty_plugins(self, plugin: str):
        excluded_plugins = [
            "embed_thumbnail",  # value is bool, not dict
            "square_thumbnail",
            "format",  # value is string, not dict
            "filter_include",  # is list
            "filter_exclude",  # is list
        ]
        if plugin not in excluded_plugins:
            self._partial_validate({plugin: {}})

    def test_error__bad_preset_section(self):
        self._partial_validate(
            preset_dict={"does_not_exist": "lol"},
            expected_error_message="Validation error in partial_preset: "
            "'partial_preset' contains the field 'does_not_exist' which is not allowed. "
            f"Allowed fields: {', '.join(sorted(PRESET_KEYS))}",
        )

    def test_error__download_args(self):
        self._partial_validate(
            preset_dict={"download": {"bad_key": "nope"}},
            expected_error_message="Validation error in partial_preset.download.1: "
            "'partial_preset.download.1' contains the field 'bad_key' which is not allowed. "
            "Allowed fields: download_reverse, include_sibling_metadata, playlist_thumbnails, "
            "source_thumbnails, url, variables, ytdl_options",
        )

    @pytest.mark.parametrize(
        "preset_dict",
        [
            {"nfo_tags": {"tags": {"key-1": {"attributes": {"test": "2"}}}}},
            {"download": [{"variables_to_set": {"name": "value"}}]},
        ],
    )
    def test_partial_validate__incomplete_list_item(self, preset_dict):
        with pytest.raises(ValidationException):
            _ = ConfigFile(
                name="test_partial_validate",
                value={
                    "configuration": {"working_directory": "."},
                    "presets": {"partial_preset": preset_dict},
                },
            )

    def test_config_file_working_dir_home_dir(self):
        out = ConfigFile(
            name="test_tilda",
            value={
                "configuration": {"working_directory": "~/working/dir"},
            },
        )

        assert out.config_options.working_directory == str(
            Path(os.path.expanduser("~")) / "working" / "dir"
        )

    @pytest.mark.parametrize(
        "preset_dict",
        [
            {"overrides": "not a dict"},
            {"overrides": ["list"]},
        ],
    )
    def test_error__bad_overrides(self, preset_dict):
        self._partial_validate(
            preset_dict=preset_dict,
            expected_error_message="Validation error in partial_preset.overrides",
        )

    @pytest.mark.parametrize(
        "preset_dict",
        [
            {"ytdl_options": "not a dict"},
            {"ytdl_options": ["list"]},
        ],
    )
    def test_error__bad_ytdl_options(self, preset_dict):
        self._partial_validate(
            preset_dict=preset_dict,
            expected_error_message="Validation error in partial_preset.ytdl_options",
        )

    @pytest.mark.parametrize(
        "preset_dict",
        [
            {"preset": "DNE"},
            {"preset": ["DNE"]},
        ],
    )
    def test_error__non_existent_preset(self, preset_dict):
        self._partial_validate(
            preset_dict=preset_dict,
            expected_error_message="Validation error in partial_preset: "
            "preset 'DNE' does not exist in the provided config.",
        )
