import tempfile
from pathlib import Path

import pytest

from ytdl_sub.utils.subtitles import SUBTITLE_EXTENSIONS
from ytdl_sub.validators.file_path_validators import StringFormatterFilePathValidator


class TestStringFormatterFilePathValidator:
    @pytest.mark.parametrize(
        "ext",
        [
            "mp4",
            "info.json",
        ]
        + [f"en-US.{ext}" for ext in SUBTITLE_EXTENSIONS],
    )
    @pytest.mark.parametrize("file_name_char", ["a", "𒃀"])
    @pytest.mark.parametrize("file_name_len", [10, 10000])
    def test_truncates_file_name_successfully(
        self, ext: str, file_name_char: str, file_name_len: int
    ):
        ext = f".{ext}"  # pytest args with . in the beginning act weird
        with tempfile.TemporaryDirectory() as temp_dir:
            file_name = (file_name_char * file_name_len) + ext
            file_path = str(Path(temp_dir) / file_name)

            formatter = StringFormatterFilePathValidator(name="test", value=str(file_path))
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
