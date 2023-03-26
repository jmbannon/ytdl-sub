import os
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Tuple

from ytdl_sub.config.defaults import MAX_FILE_NAME_BYTES
from ytdl_sub.utils.file_handler import get_file_extension
from ytdl_sub.utils.subtitles import SUBTITLE_EXTENSIONS
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


class FilePathValidatorMixin:
    _EXTENSION_BYTES = len("-thumb.jpg".encode("utf-8")) + 8
    _DEFAULT_MAX_BASE_FILE_NAME_BYTES: int = MAX_FILE_NAME_BYTES - _EXTENSION_BYTES

    _MAX_BASE_FILE_NAME_BYTES: int = _DEFAULT_MAX_BASE_FILE_NAME_BYTES

    @classmethod
    def set_max_file_name_bytes(cls, max_file_name_bytes: int) -> None:
        """Actually sets the max _base_ file name in bytes (excludes extension)"""
        max_base_file_name_bytes = max_file_name_bytes - cls._EXTENSION_BYTES

        # bound between (extension_bytes + 20, MAX_FILE_NAME_BYTES)
        max_base_file_name_bytes = max(max_base_file_name_bytes, 16)
        max_base_file_name_bytes = min(
            max_base_file_name_bytes, MAX_FILE_NAME_BYTES - cls._EXTENSION_BYTES
        )

        cls._MAX_BASE_FILE_NAME_BYTES = max_base_file_name_bytes

    @classmethod
    def _is_file_name_too_long(cls, file_name: str) -> bool:
        return len(file_name.encode("utf-8")) > cls._MAX_BASE_FILE_NAME_BYTES

    @classmethod
    def _get_extension_split(cls, file_name: str) -> Tuple[str, str]:
        ext = get_file_extension(file_name)
        return file_name[: -len(ext)], ext

    @classmethod
    def _truncate_file_name(cls, file_name: str) -> str:
        file_sub_name, file_ext = cls._get_extension_split(file_name)

        desired_size = cls._MAX_BASE_FILE_NAME_BYTES - len(file_ext.encode("utf-8")) - 1
        while len(file_sub_name.encode("utf-8")) > desired_size:
            file_sub_name = file_sub_name[:-1]

        return f"{file_sub_name}.{file_ext}"

    @classmethod
    def _maybe_truncate_file_path(cls, file_path: Path) -> str:
        """Turn into a Path, then a string, to get correct directory separators"""
        file_directory, file_name = os.path.split(Path(file_path))

        if cls._is_file_name_too_long(file_name):
            return str(Path(file_directory) / cls._truncate_file_name(file_name))

        return str(file_path)


# pylint: disable=line-too-long
class StringFormatterFileNameValidator(StringFormatterValidator, FilePathValidatorMixin):
    """
    Same as a
    :class:`StringFormatterValidator <ytdl_sub.validators.string_formatter_validators.StringFormatterValidator>`
    but ensures the file name does not exceed the OS limit (typically 255 bytes). If it does exceed,
    it will preserve the extension and truncate the end of the file name.
    """

    # pylint: enable=line-too-long

    _expected_value_type_name = "filepath"

    @classmethod
    def _is_file_name_too_long(cls, file_name: str) -> bool:
        return len(file_name.encode("utf-8")) > cls._MAX_BASE_FILE_NAME_BYTES

    @classmethod
    def _get_extension_split(cls, file_name: str) -> Tuple[str, str]:
        """
        Returns
        -------
        file_name, ext (including .)
        """
        if file_name.endswith(".info.json"):
            ext = ".info.json"
        elif file_name.endswith("-thumb.jpg"):
            ext = "-thumb.jpg"
        elif any(file_name.endswith(f".{subtitle_ext}") for subtitle_ext in SUBTITLE_EXTENSIONS):
            file_name_split = file_name.split(".")
            ext = file_name_split[-1]

            # Try to capture .lang.ext
            if len(file_name_split) > 2 and len(file_name_split[-2]) < 6:
                ext = f".{file_name_split[-2]}.{file_name_split[-1]}"
        else:
            ext = f".{file_name.rsplit('.', maxsplit=1)[-1]}"

        return file_name[: -len(ext)], ext

    @classmethod
    def _truncate_file_name(cls, file_name: str) -> str:
        file_sub_name, file_ext = cls._get_extension_split(file_name)

        while len(file_sub_name.encode("utf-8")) > cls._MAX_BASE_FILE_NAME_BYTES:
            file_sub_name = file_sub_name[:-1]

        return f"{file_sub_name}{file_ext}"

    def apply_formatter(self, variable_dict: Dict[str, str]) -> str:
        """Turn into a Path, then a string, to get correct directory separators"""
        file_path = Path(super().apply_formatter(variable_dict))
        return self._maybe_truncate_file_path(file_path)


class OverridesStringFormatterFilePathValidator(OverridesStringFormatterValidator):
    _expected_value_type_name = "static filepath"

    def apply_formatter(self, variable_dict: Dict[str, str]) -> str:
        """Turn into a Path, then a string, to get correct directory separators"""
        return os.path.realpath(super().apply_formatter(variable_dict))
