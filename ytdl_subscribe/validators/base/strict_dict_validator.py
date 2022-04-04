from typing import List
from typing import Set

from ytdl_subscribe.validators.base.validators import DictValidator
from ytdl_subscribe.validators.exceptions import ValidationException


class StrictDictValidator(DictValidator):
    """
    Validates dictionary-based fields with required and optional keys.
    """

    required_keys: Set[str] = set()
    optional_keys: Set[str] = set()
    allow_extra_keys = False

    def __init__(self, name, value):
        super().__init__(name, value)

        if len(self.allowed_keys) == 0:
            raise ValueError(
                "No required or optional keys defined when using a StrictDictValidator. "
                "Should be using DictValidator instead."
            )

        # Ensure all required keys are present
        for required_key in self.required_keys:
            if required_key not in self.value:
                raise self._validation_exception(
                    f"missing the required field '{required_key}'"
                )

        # Ensure an empty dict was not passed as the value
        if not self.dict:
            raise self._validation_exception(
                f"at least one of the following fields must be defined: "
                f"{', '.join(self.optional_keys)}'"
            )

        # Ensure all keys are either required or optional keys if no extra field are allowed
        if not self.allow_extra_keys:
            for object_key in self.keys:
                if object_key not in self.allowed_keys:
                    error_msg = (
                        f"'{self.name}' contains the field '{object_key}' which is not allowed. "
                        f"Allowed fields: {', '.join(self.allowed_keys)}"
                    )
                    raise ValidationException(error_msg)

    @property
    def allowed_keys(self) -> List[str]:
        """
        Returns
        -------
        Sorted list of required and optional keys
        """
        return sorted(list(self.required_keys.union(self.optional_keys)))
