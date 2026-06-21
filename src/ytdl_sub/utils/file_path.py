import os
import posixpath
from pathlib import Path
from typing import Tuple

from ytdl_sub.config.defaults import MAX_FILE_NAME_BYTES
from ytdl_sub.utils.file_handler import get_file_extension


class FilePathTruncater:
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
    def _get_extension_split(cls, file_name: str) -> Tuple[str, str, str]:
        if file_name.endswith("-thumb.jpg"):
            ext = "-thumb.jpg"
            delimiter = ""
        else:
            ext = get_file_extension(file_name)
            delimiter = "."

        return file_name[: -len(ext)], ext, delimiter

    @classmethod
    def _truncate_file_name(cls, file_name: str) -> str:
        file_sub_name, file_ext, delimiter = cls._get_extension_split(file_name)

        desired_size = cls._MAX_BASE_FILE_NAME_BYTES - len(file_ext.encode("utf-8")) - 1
        while len(file_sub_name.encode("utf-8")) > desired_size:
            file_sub_name = file_sub_name[:-1]

        return f"{file_sub_name}{delimiter}{file_ext}"

    @classmethod
    def _truncate_directory_name(cls, directory_name: str) -> str:
        while len(directory_name.encode("utf-8")) > cls._MAX_BASE_FILE_NAME_BYTES:
            directory_name = directory_name[:-1]

        return directory_name

    @classmethod
    def maybe_truncate_file_path(cls, file_path: str) -> str:
        """Turn into a Path, then a string, to get correct directory separators"""
        file_directory, file_name = os.path.split(Path(file_path))

        if cls._is_file_name_too_long(file_name):
            return str(Path(file_directory) / cls._truncate_file_name(file_name))

        return str(file_path)

    @classmethod
    def maybe_truncate_file_name_path(cls, file_name_path: str) -> str:
        """
        Truncates each component of a relative output file name path. Both the
        subdirectories (which can be derived from metadata such as the title) and the
        final file name are truncated if they exceed the OS limit. The file name's
        extension is always preserved.
        """
        parts = Path(file_name_path).parts
        if not parts:
            return file_name_path

        *directory_parts, file_name = parts

        truncated_parts = [
            cls._truncate_directory_name(part) if cls._is_file_name_too_long(part) else part
            for part in directory_parts
        ]

        if cls._is_file_name_too_long(file_name):
            file_name = cls._truncate_file_name(file_name)

        return str(Path(*truncated_parts, file_name))

    @classmethod
    def to_native_filepath(cls, file_path: str) -> str:
        """Ensures file paths use the correct separator"""
        return os.path.expanduser(file_path.replace(posixpath.sep, os.sep))
