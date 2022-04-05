from typing import Any

from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.validators import StringValidator


class ConfigOptionsValidator(StrictDictValidator):
    """Validation for the config options"""

    _required_keys = {"working_directory"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        self.working_directory = self._validate_key(
            key="working_directory", validator=StringValidator
        )
