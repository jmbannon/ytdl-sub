from typing import Any
from typing import Dict
from typing import Optional
from typing import Set
from typing import Type
from typing import TypeVar

from ytdl_subscribe.validators.base.validator import Validator
from ytdl_subscribe.validators.exceptions import ValidationException

T = TypeVar("T", bound=Validator)


class DictValidator(Validator):

    expected_value_type = dict
    expected_value_type_name = "object"  # for non-python users

    required_fields: Set[str] = set()
    optional_fields: Set[str] = set()

    _allow_extra_fields = False

    def __init__(self, name, value):
        super().__init__(name, value)

        # Ensure all required keys are present
        for required_key in self.required_fields:
            if required_key not in self.value:
                error_msg = (
                    f"'{self.name}' is missing the required field '{required_key}'"
                )
                raise ValidationException(error_msg)

        # If no extra fields are allowed, ensure all fields are either
        # required or optional fields
        if not self._allow_extra_fields:
            for object_key in self.object_keys:
                if object_key not in self.allowed_fields:
                    error_msg = (
                        f"'{self.name}' contains the field '{object_key}' which is not allowed. "
                        f"Allowed fields: {', '.join(self.allowed_fields)}"
                    )
                    raise ValidationException(error_msg)

    def validate_dict_value(
        self, dict_value_name: str, validator: Type[T], default: Optional[Any] = None
    ) -> T:
        value = self.get(object_key=dict_value_name, default=default)
        if value is None:
            raise self._validation_exception(
                f"{dict_value_name} is missing when it should be present."
            )

        return validator(
            name=f"{self.name}.{dict_value_name}",
            value=self.get(object_key=dict_value_name, default=default),
        )

    @property
    def dict(self) -> dict:
        return self._value

    @property
    def allowed_fields(self):
        return sorted(self.required_fields.union(self.optional_fields))

    @property
    def object_keys(self):
        return sorted(list(self.dict.keys()))

    @property
    def object_items(self):
        return self.dict.items()

    def get(self, object_key: str, default: Optional[Any] = None) -> Any:
        return self.dict.get(object_key, default)


class DictWithExtraFieldsValidator(DictValidator):
    _allow_extra_fields = True
