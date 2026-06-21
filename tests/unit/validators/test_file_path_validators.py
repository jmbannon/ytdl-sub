import os
import tempfile
from pathlib import Path

import pytest

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.defaults import MAX_FILE_NAME_BYTES
from ytdl_sub.script.script import Script
from ytdl_sub.utils.file_path import FilePathTruncater
from ytdl_sub.utils.subtitles import SUBTITLE_EXTENSIONS
from ytdl_sub.validators.file_path_validators import StringFormatterFileNameValidator


@pytest.mark.usefixtures("register_custom_functions")
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
            truncated_file_path = formatter.post_process(
                Script({"file_name": formatter.format_string}).resolve().get_str("file_name")
            )

            _, truncated_file_name = os.path.split(truncated_file_path)
            assert truncated_file_name.count(".") == ext.count(".")
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

        base_file_name = "s2023.e031701 - 𝗪𝗔𝗥𝗡𝗜𝗡𝗚： {LG} Secretly Overhaul This OLED Feature on C３ & G３… Should You Buy C２ Instead？"

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = str(Path(temp_dir) / f"{base_file_name}{ext}")

            formatter = StringFormatterFileNameValidator(name="test", value="")
            truncated_file_path = formatter.post_process(file_path)

            assert truncated_file_path == str(
                Path(temp_dir)
                / f"s2023.e031701 - 𝗪𝗔𝗥𝗡𝗜𝗡𝗚： {{LG}} Secretly Overhaul This OLED Feature on C３ & G３… Should You Buy C２ Instead？{ext}"
            )

            # Ensure it can actually open the file
            with open(truncated_file_path, "w", encoding="utf-8"):
                # Make sure the file is actually in the directory
                dir_paths = list(Path(temp_dir).rglob("*"))

                assert len(dir_paths) == 1
                assert Path(truncated_file_path) == dir_paths[0]

    @pytest.mark.parametrize("ext", ["mp4", "-thumb.jpg"])
    def test_truncates_subdirectory_in_file_name_path(self, ext: str):
        if "thumb" not in ext:  # do not put . in front of -thumb
            ext = f".{ext}"

        # Mathematical bold unicode characters are 4 bytes each in UTF-8, so a title used
        # as a subdirectory can easily exceed the OS file name limit (typically 255 bytes).
        long_directory = (
            "[2026] 𝗿𝘁𝗶𝘀𝘁 𝗢𝗻𝗲 - 𝗔 𝗩𝗲𝗿𝘆 𝗟𝗼𝗻𝗴 𝗦𝗼𝗻𝗴 𝗧𝗶𝘁𝗹𝗲 "
            "𝗧𝗵𝗮𝘁 𝗘𝘅𝗰𝗲𝗲𝗱𝘀 𝗧𝗵𝗲 𝗟𝗶𝗺𝗶𝘁 (𝗘𝘅𝘁𝗲𝗻𝗱𝗲𝗱 𝗠𝗶𝘅 𝘅 "
            "𝗦𝗲𝗰𝗼𝗻𝗱 𝗔𝗿𝘁𝗶𝘀𝘁 & 𝗧𝗵𝗶𝗿𝗱 𝗔𝗿𝘁𝗶𝘀𝘁)"
        )
        # Sanity check that the directory really does exceed the limit
        assert len(long_directory.encode("utf-8")) > FilePathTruncater._MAX_BASE_FILE_NAME_BYTES

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = str(Path(temp_dir) / long_directory / f"video{ext}")

            formatter = StringFormatterFileNameValidator(name="test", value="")
            truncated_file_path = formatter.post_process(file_path)

            truncated_directory, truncated_file_name = os.path.split(truncated_file_path)
            _, truncated_directory_name = os.path.split(truncated_directory)

            # Both the subdirectory and the file name must fit within the OS limit
            assert (
                len(truncated_directory_name.encode("utf-8"))
                <= FilePathTruncater._MAX_BASE_FILE_NAME_BYTES
            )
            assert (
                len(truncated_file_name.encode("utf-8"))
                <= FilePathTruncater._MAX_BASE_FILE_NAME_BYTES
            )
            assert truncated_file_name.endswith(ext)

            # The original bug raised "OSError: [Errno 36] Filename too long" here because
            # the subdirectory component was never truncated.
            os.makedirs(truncated_directory, exist_ok=True)
            assert os.path.isdir(truncated_directory)

    @pytest.mark.parametrize(
        "file_name_max_bytes, expected_max",
        [
            (50, 50 - FilePathTruncater._EXTENSION_BYTES),
            (0, 16),
            (10000, MAX_FILE_NAME_BYTES - FilePathTruncater._EXTENSION_BYTES),
        ],
    )
    def test_config_changes_max_file_name_bytes(self, file_name_max_bytes: int, expected_max: int):
        # Ensure the default is set
        assert (
            FilePathTruncater._MAX_BASE_FILE_NAME_BYTES
            == FilePathTruncater._DEFAULT_MAX_BASE_FILE_NAME_BYTES
        )

        try:
            # Initializes the config values, setting the max to 10 bytes
            _ = ConfigFile.from_dict(
                {
                    "configuration": {
                        "working_directory": ".",
                        "file_name_max_bytes": file_name_max_bytes,
                    },
                    "presets": {},
                }
            )

            assert FilePathTruncater._MAX_BASE_FILE_NAME_BYTES == expected_max
        finally:
            FilePathTruncater._MAX_BASE_FILE_NAME_BYTES = (
                FilePathTruncater._DEFAULT_MAX_BASE_FILE_NAME_BYTES
            )
