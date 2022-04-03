from typing import Any
from typing import Optional
from typing import Type
from typing import TypeVar

from ytdl_subscribe.validators.exceptions import ValidationException


class Validator:
    # The python type that value should be
    expected_value_type: Type = object

    # When raising an error, call the type this value instead of its python name
    expected_value_type_name: Optional[str] = None

    def __validate_value(self):
        """
        Returns
        -------
        Validation exception to raise when the value's type is not the expected type
        """
        if not isinstance(self._value, self.expected_value_type):
            expected_value_type_name = self.expected_value_type_name or str(
                self.expected_value_type
            )
            raise self._validation_exception(
                error_message=f"should be of type {expected_value_type_name}."
            )

    def __init__(self, name: str, value: Any):
        self.name = name
        self._value = value

        self.__validate_value()

    @property
    def value(self) -> object:
        return self._value

    def _validation_exception(self, error_message: str):
        prefix = f"Validation error in {self.name}: "
        return ValidationException(f"{prefix}{error_message}")


class BoolValidator(Validator):
    expected_value_type: Type = bool
    expected_value_type_name = "boolean"

    @property
    def value(self) -> bool:
        return self._value


class StringValidator(Validator):
    expected_value_type: Type = str
    expected_value_type_name = "string"

    @property
    def value(self) -> str:
        return self._value


T = TypeVar("T", bound=Validator)


class DictValidator(Validator):
    expected_value_type = dict
    expected_value_type_name = "object"  # for non-python users

    @property
    def dict(self) -> dict:
        return self._value

    @property
    def keys(self):
        return sorted(list(self.dict.keys()))

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self.dict.get(key, default)

    def validate_key(
        self, key: str, validator: Type[T], default: Optional[Any] = None
    ) -> T:
        value = self.get(key=key, default=default)
        if value is None:
            raise self._validation_exception(
                f"{key} is missing when it should be present."
            )

        return validator(
            name=f"{self.name}.{key}",
            value=self.get(key=key, default=default),
        )
