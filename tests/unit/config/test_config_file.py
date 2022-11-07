import re
from typing import Dict
from typing import Optional

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.preset import PRESET_KEYS
from ytdl_sub.config.preset_class_mappings import DownloadStrategyMapping
from ytdl_sub.config.preset_class_mappings import PluginMapping
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
        self._partial_validate({plugin: {}})

    @pytest.mark.parametrize("source", DownloadStrategyMapping.sources())
    def test_success__empty_sources(self, source: str):
        for download_strategy in DownloadStrategyMapping.source_download_strategies(source):
            self._partial_validate({source: {"download_strategy": download_strategy}})

    def test_error__bad_preset_section(self):
        self._partial_validate(
            preset_dict={"does_not_exist": "lol"},
            expected_error_message="Validation error in partial_preset: "
            "'partial_preset' contains the field 'does_not_exist' which is not allowed. "
            f"Allowed fields: {', '.join(sorted(PRESET_KEYS))}",
        )

    def test_error__multiple_sources(self):
        self._partial_validate(
            preset_dict={"youtube": {}, "download": {}},
            expected_error_message="Validation error in partial_preset: "
            "Contains the sources download, youtube but can only have one",
        )

    def test_error__no_download_strategy(self):
        self._partial_validate(
            preset_dict={"download": {}},
            expected_error_message="Validation error in partial_preset.download: "
            "missing the required field 'download_strategy'",
        )

    def test_error__bad_download_strategy(self):
        self._partial_validate(
            preset_dict={"download": {"download_strategy": "fail"}},
            expected_error_message="Validation error in partial_preset.download: "
            "Tried to use download strategy 'fail' with source 'download', "
            "which does not exist. Available download strategies: multi_url, url",
        )

    def test_error__bad_download_strategy_args(self):
        self._partial_validate(
            preset_dict={"download": {"download_strategy": "multi_url", "bad_key": "nope"}},
            expected_error_message="Validation error in partial_preset.download: "
            "'partial_preset.download' contains the field 'bad_key' which is not allowed. "
            "Allowed fields: urls",
        )

    @pytest.mark.parametrize(
        "preset_dict",
        [
            {"nfo_tags": {"tags": {"key-1": {"attributes": {"test": "2"}}}}},
            {"download": {"urls": [{"variables_to_set": {"name": "value"}}]}},
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

    @pytest.mark.parametrize(
        "preset_dict",
        [
            {"overrides": "not a dict"},
            {"overrides": {"nested": {"dict": "value"}}},
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
