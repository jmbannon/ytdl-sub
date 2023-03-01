import os
from pathlib import Path
from typing import Dict

from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator, OverridesStringFormatterValidator


class StringFormatterFilePathValidator(StringFormatterValidator):
    _expected_value_type_name = "filepath"

    def apply_formatter(self, variable_dict: Dict[str, str]) -> str:
        return str(Path(super().apply_formatter(variable_dict)))


class OverridesStringFormatterValidatorFilePathValidator(OverridesStringFormatterValidator):
    _expected_value_type_name = "static filepath"

    def apply_formatter(self, variable_dict: Dict[str, str]) -> str:
        return os.path.realpath(super().apply_formatter(variable_dict))
