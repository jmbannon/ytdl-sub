from typing import Any
from typing import Optional
from typing import Type

from ytdl_subscribe.validators.base.validator import Validator
from ytdl_subscribe.validators.exceptions import ValidationException


class BoolValidator(Validator):
    expected_value_type: Type = bool
    expected_value_type_name = "boolean"
