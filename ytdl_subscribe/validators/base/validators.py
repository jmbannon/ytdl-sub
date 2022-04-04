from typing import Any
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from ytdl_subscribe.validators.exceptions import ValidationException


class Validator:
    """
    Used to validate the value of a python object. This is the 'base' class that will first
    check that the value's type matches the expected type. Validators that inherit from this should
    perform their validation within the __init__.
    """

    # If the value is not this expected type, error
    expected_value_type: Type = object

    # When raising an error, call the type this value instead of its python name
    expected_value_type_name: Optional[str] = None

    def __init__(self, name: str, value: Any):
        self.name = name
        self._value = value

        if not isinstance(self._value, self.expected_value_type):
            expected_value_type_name = self.expected_value_type_name or str(
                self.expected_value_type
            )
            raise self._validation_exception(
                error_message=f"should be of type {expected_value_type_name}."
            )

    @property
    def value(self) -> object:
        """
        Returns
        -------
        Value of the validator
        """
        return self._value

    def _validation_exception(self, error_message: str) -> ValidationException:
        """
        Parameters
        ----------
        error_message
            Error message to include in the ValidationException

        Returns
        -------
        Validation exception with a consistent prefix.
        """
        prefix = f"Validation error in {self.name}: "
        return ValidationException(f"{prefix}{error_message}")


class BoolValidator(Validator):
    """
    Validates boolean fields.
    """

    expected_value_type: Type = bool
    expected_value_type_name = "boolean"

    @property
    def value(self) -> bool:
        """
        Returns
        -------
        Boolean value
        """
        return self._value


class StringValidator(Validator):
    """
    Validates string fields.
    """

    expected_value_type: Type = str
    expected_value_type_name = "string"

    @property
    def value(self) -> str:
        """
        Returns
        -------
        String value
        """
        return self._value


T = TypeVar("T", bound=Validator)


class DictValidator(Validator):
    """
    Validates dictionary-based fields. Errors to them as 'object's since this could be validating
    a yaml.
    """

    expected_value_type = dict
    expected_value_type_name = "object"

    @property
    def dict(self) -> dict:
        """
        Returns
        -------
        Dictionary value
        """
        return self._value

    @property
    def keys(self) -> List[str]:
        """
        Returns
        -------
        Sorted list of dictionary keys
        """
        return sorted(list(self.dict.keys()))

    def validate_key(
        self,
        key: str,
        validator: Type[T],
        default: Optional[Any] = None,
    ) -> T:
        """
        Parameters
        ----------
        key
            Name of they key in the dict to validate
        validator
            The validator to use for the key's value
        default
            If the key's value is None, use this as the default

        Returns
        -------
        An instance of the specified validator
        """
        value = self.dict.get(key, default)
        if value is None:
            raise self._validation_exception(
                f"{key} is missing when it should be present."
            )

        return validator(
            name=f"{self.name}.{key}",
            value=value,
        )

    def validate_key_if_present(
        self,
        key: str,
        validator: Type[T],
        default: Optional[Any] = None,
    ) -> Optional[T]:
        if key not in self.dict:
            return None

        return self.validate_key(key=key, validator=validator, default=default)
