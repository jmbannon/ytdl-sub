from typing import Any
from typing import Dict
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
    _expected_value_type: Type = object

    # When raising an error, call the type this value instead of its python name
    _expected_value_type_name: Optional[str] = None

    def __init__(self, name: str, value: Any):
        self._name = name
        self._value = value

        if not isinstance(self._value, self._expected_value_type):
            expected_value_type_name = self._expected_value_type_name or str(
                self._expected_value_type
            )
            raise self._validation_exception(
                error_message=f"should be of type {expected_value_type_name}."
            )

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
        prefix = f"Validation error in {self._name}: "
        return ValidationException(f"{prefix}{error_message}")


class BoolValidator(Validator):
    """
    Validates boolean fields.
    """

    _expected_value_type: Type = bool
    _expected_value_type_name = "boolean"

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

    _expected_value_type = str
    _expected_value_type_name = "string"

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

    _expected_value_type = dict
    _expected_value_type_name = "object"

    @property
    def _dict(self) -> dict:
        """
        Returns
        -------
        Dictionary value
        """
        return self._value

    @property
    def _keys(self) -> List[str]:
        """
        Returns
        -------
        Sorted list of dictionary keys
        """
        return sorted(list(self._dict.keys()))

    def _validate_key(
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
        value = self._dict.get(key, default)
        if value is None:
            raise self._validation_exception(
                f"{key} is missing when it should be present."
            )

        return validator(
            name=f"{self._name}.{key}",
            value=value,
        )

    def _validate_key_if_present(
        self,
        key: str,
        validator: Type[T],
        default: Optional[Any] = None,
    ) -> Optional[T]:
        if key not in self._dict:
            return None

        return self._validate_key(key=key, validator=validator, default=default)


class LiteralDictValidator(DictValidator):
    """DictValidator with exposed dict and keys method"""

    @property
    def dict(self) -> Dict:
        return super()._dict

    @property
    def keys(self) -> List[str]:
        return super()._keys
