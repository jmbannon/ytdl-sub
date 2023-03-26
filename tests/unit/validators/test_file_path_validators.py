import tempfile
from pathlib import Path

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.config_validator import DEFAULT_MAX_FILE_NAME_BYTES
from ytdl_sub.utils.subtitles import SUBTITLE_EXTENSIONS
from ytdl_sub.validators.file_path_validators import StringFormatterFileNameValidator, \
    FilePathValidatorMixin


class TestStringFormatterFilePathValidator:
    @pytest.mark.parametrize(
        "ext",
        ["mp4", "info.json", "-thumb.jpg"] + [f"en-US.{ext}" for ext in SUBTITLE_EXTENSIONS],
    )
    @pytest.mark.parametrize("file_name_char", ["a", "𒃀"])
    @pytest.mark.parametrize("file_name_len", [10, 10000])
    def test_truncates_file_name_successfully(
        self, ext: str, file_name_char: str, file_name_len: int
    ):
        if "thumb" not in ext:  # do not put . in front of -thumb
            ext = f".{ext}"  # pytest args with . in the beginning act weird

        with tempfile.TemporaryDirectory() as temp_dir:
            file_name = (file_name_char * file_name_len) + ext
            file_path = str(Path(temp_dir) / file_name)

            formatter = StringFormatterFileNameValidator(name="test", value=str(file_path))
            truncated_file_path = formatter.apply_formatter({})

            assert truncated_file_path.count(".") == ext.count(".")
            assert str(Path(temp_dir)) in truncated_file_path
            assert ext in truncated_file_path

            # Ensure it can actually open the file
            with open(truncated_file_path, "w", encoding="utf-8"):
                # Make sure the file is actually in the directory
                dir_paths = list(Path(temp_dir).rglob("*"))

                assert len(dir_paths) == 1
                assert Path(truncated_file_path) == dir_paths[0]

    @pytest.mark.parametrize(
        "ext",
        ["mp4", "info.json", "-thumb.jpg"] + [f"en-US.{ext}" for ext in SUBTITLE_EXTENSIONS],
    )
    def test_truncates_file_names_successfully(self, ext: str):
        if "thumb" not in ext:  # do not put . in front of -thumb
            ext = f".{ext}"  # pytest args with . in the beginning act weird

        base_file_name = "s2023.e031701 - 𝗪𝗔𝗥𝗡𝗜𝗡𝗚： LG Secretly Overhaul This OLED Feature on C３ & G３… Should You Buy C２ Instead？"

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = str(Path(temp_dir) / f"{base_file_name}{ext}")

            formatter = StringFormatterFileNameValidator(name="test", value=str(file_path))
            truncated_file_path = formatter.apply_formatter({})

            assert truncated_file_path == str(
                Path(temp_dir)
                / f"s2023.e031701 - 𝗪𝗔𝗥𝗡𝗜𝗡𝗚： LG Secretly Overhaul This OLED Feature on C３ & G３… Should You Buy C２ Instead？{ext}"
            )

            # Ensure it can actually open the file
            with open(truncated_file_path, "w", encoding="utf-8"):
                # Make sure the file is actually in the directory
                dir_paths = list(Path(temp_dir).rglob("*"))

                assert len(dir_paths) == 1
                assert Path(truncated_file_path) == dir_paths[0]

    def test_config_changes_max_file_name_bytes(self):
        # Ensure the default is set
        assert FilePathValidatorMixin.MAX_FILE_NAME_BYTES == DEFAULT_MAX_FILE_NAME_BYTES

        try:
            # Initializes the config values, setting the max to 10 bytes
            _ = ConfigFile.from_dict({
                "working_directory": ".",
                "file_name_max_bytes": 10,
            })

            assert FilePathValidatorMixin.MAX_FILE_NAME_BYTES == 10
        finally:
            FilePathValidatorMixin.MAX_FILE_NAME_BYTES = DEFAULT_MAX_FILE_NAME_BYTES
