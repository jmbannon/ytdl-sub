import os
from pathlib import Path
from typing import Any

from ytdl_sub.script.script import Script
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


# pylint: disable=line-too-long
class StringFormatterFileNameValidator(StringFormatterValidator):
    """
    Same as a
    :class:`StringFormatterValidator <ytdl_sub.validators.string_formatter_validators.StringFormatterValidator>`
    but ensures the file name does not exceed the OS limit (typically 255 bytes). If it does exceed,
    it will preserve the extension and truncate the end of the file name.
    """

    # pylint: enable=line-too-long

    _expected_value_type_name = "filepath"

    def post_process(self, resolved: str) -> str:
        return (
            Script(
                {
                    "tmp_var_1": resolved,
                    "tmp_var_2": "{%to_native_filepath(%truncate_filepath_if_too_long(tmp_var_1))}",
                }
            )
            .resolve()
            .get_str("tmp_var_2")
        )


class OverridesStringFormatterFilePathValidator(OverridesStringFormatterValidator):
    _expected_value_type_name = "static filepath"

    def post_process(self, resolved: str) -> str:
        return (
            Script(
                {
                    "tmp_var_1": resolved,
                    "tmp_var_2": "{%to_native_filepath(%truncate_filepath_if_too_long(tmp_var_1))}",
                }
            )
            .resolve()
            .get_str("tmp_var_2")
        )
