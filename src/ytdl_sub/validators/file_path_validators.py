import os
from pathlib import Path
from typing import Any
from typing import Dict

from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import StringValidator


class ExistingFileValidator(StringValidator):
    _expected_value_type_name = "file"

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)
        if not os.path.isfile(self._value):
            raise self._validation_exception(
                f"Expects an existing file, but '{self.value}' is not a file"
            )

    @property
    def value(self) -> str:
        """Turn into a Path, then a string, to get correct directory separators"""
        return str(Path(self._value))


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
