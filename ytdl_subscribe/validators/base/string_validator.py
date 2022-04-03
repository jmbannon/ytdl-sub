from typing import Any
from typing import Optional
from typing import Type

from ytdl_subscribe.validators.base.validator import Validator
from ytdl_subscribe.validators.exceptions import ValidationException


class StringValidator(Validator):
    expected_value_type: Type = str
    expected_value_type_name = "string"

    @property
    def value(self) -> str:
        return self._value
