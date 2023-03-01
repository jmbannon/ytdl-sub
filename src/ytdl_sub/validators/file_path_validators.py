import os
from pathlib import Path
from typing import Dict

from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator


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
