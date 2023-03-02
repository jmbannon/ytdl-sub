import os
from pathlib import Path
from typing import Any
from typing import Dict

from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import StringValidator


class FFmpegFileValidator(StringValidator):
    _expected_value_type_name = "ffmpeg dependency"
    _ffmpeg_dependency = "ffmpeg"

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)
        if not os.path.isfile(self.value):
            raise self._validation_exception(
                f"Expects an {self._ffmpeg_dependency} executable at '{self.value}', but "
                f"does not exist. See https://github.com/jmbannon/ytdl-sub#installation on how "
                f"to install ffmpeg dependencies."
            )

    @property
    def value(self) -> str:
        """Turn into a Path, then a string, to get correct directory separators"""
        return str(Path(self._value))


class FFprobeFileValidator(FFmpegFileValidator):
    _ffmpeg_dependency = "ffprobe"


class StringFormatterFilePathValidator(StringFormatterValidator):
    _expected_value_type_name = "filepath"

    def apply_formatter(self, variable_dict: Dict[str, str]) -> str:
        """Turn into a Path, then a string, to get correct directory separators"""
        return str(Path(super().apply_formatter(variable_dict)))


class OverridesStringFormatterValidatorFilePathValidator(OverridesStringFormatterValidator):
    _expected_value_type_name = "static filepath"

    def apply_formatter(self, variable_dict: Dict[str, str]) -> str:
        """Turn into a Path, then a string, to get correct directory separators"""
        return os.path.realpath(super().apply_formatter(variable_dict))
