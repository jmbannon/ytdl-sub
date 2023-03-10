import tempfile
from pathlib import Path

import pytest

from ytdl_sub.utils.subtitles import SUBTITLE_EXTENSIONS
from ytdl_sub.validators.file_path_validators import StringFormatterFilePathValidator


class TestStringFormatterFilePathValidator:
    @pytest.mark.parametrize(
        "ext",
        [
            ".mp4",
            ".info.json",
        ]
        + [f".en.{ext}" for ext in SUBTITLE_EXTENSIONS],
    )
    def test_truncates_file_name_successfully(self, ext: str):
        ext = ".info.json"
        with tempfile.TemporaryDirectory() as temp_dir:
            file_name = ("a" * 10000) + ext
            file_path = str(Path(temp_dir) / file_name)

            formatter = StringFormatterFilePathValidator(name="test", value=str(file_path))
            truncated_file_path = formatter.apply_formatter({})

            assert truncated_file_path.count(".") == ext.count(".")
            assert str(Path(temp_dir)) in truncated_file_path
            assert ext in truncated_file_path

            # Ensure it can actually open the file
            with open(truncated_file_path, "w", encoding="utf-8"):
                pass
