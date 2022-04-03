from typing import Set

from ytdl_subscribe.validators.base.validators import DictValidator
from ytdl_subscribe.validators.exceptions import ValidationException


class StrictDictValidator(DictValidator):
    required_keys: Set[str] = set()
    optional_keys: Set[str] = set()

    allow_extra_fields = False

    def __init__(self, name, value):
        super().__init__(name, value)

        if len(self.required_keys) == 0:
            raise ValueError(
                "No required fields when using a StrictDictValidator. Should be using DictValidator instead."
            )

        # Ensure all required keys are present
        for required_key in self.required_keys:
            if required_key not in self.value:
                error_msg = (
                    f"'{self.name}' is missing the required field '{required_key}'"
                )
                raise ValidationException(error_msg)

        # Ensure all keys are either required or optional keys if no extra field are allowed
        if not self.allow_extra_fields:
            for object_key in self.keys:
                if object_key not in self.allowed_keys:
                    error_msg = (
                        f"'{self.name}' contains the field '{object_key}' which is not allowed. "
                        f"Allowed fields: {', '.join(self.allowed_keys)}"
                    )
                    raise ValidationException(error_msg)

    @property
    def allowed_keys(self):
        return sorted(self.required_keys.union(self.optional_keys))
