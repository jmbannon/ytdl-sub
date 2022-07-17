import copy
from abc import ABC
from typing import Any
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import final

from ytdl_sub.utils.exceptions import ValidationException

V = TypeVar("V", bound=ValidationException)


class Validator(ABC):
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
        self._value = copy.deepcopy(value)  # Always deep copy to avoid editing references

        if not isinstance(self._value, self._expected_value_type):
            expected_value_type_name = self._expected_value_type_name or str(
                self._expected_value_type
            )
            raise self._validation_exception(
                error_message=f"should be of type {expected_value_type_name}."
            )

    def _validation_exception(
        self, error_message: str | Exception, exception_class: Type[V] = ValidationException
    ) -> V:
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
        return exception_class(f"{prefix}{error_message}")


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


class ListValidator(Validator, ABC, Generic[T]):
    """
    Validates a list of objects to validate
    """

    _expected_value_type = list
    _expected_value_type_name = "list"

    _inner_list_type: Type[T]

    def __init__(self, name, value):
        super().__init__(name, value)
        self._list: List[T] = [
            self._inner_list_type(name=f"{name}.{i+1}", value=val)
            for i, val in enumerate(self._value)
        ]

    @property
    def list(self) -> List[T]:
        """
        Returns
        -------
        The list
        """
        return self._list


class DictValidator(Validator):
    """
    Validates dictionary-based fields. Errors to them as 'object's since this could be validating
    a yaml.
    """

    _expected_value_type = dict
    _expected_value_type_name = "object"

    def __init__(self, name, value):
        super().__init__(name, value)
        self.__validator_dict: Dict[str, Validator] = {}

    @final
    @property
    def _dict(self) -> dict:
        """
        Returns
        -------
        Dictionary value
        """
        return self._value

    @final
    @property
    def _validator_dict(self) -> Dict[str, Validator]:
        """
        Returns dict containing names and validators of any keys that were validated.
        This allows top-level validators to recursively search a dict validator.
        """
        return self.__validator_dict

    @final
    @property
    def _keys(self) -> List[str]:
        """
        Returns
        -------
        Sorted list of dictionary keys
        """
        return sorted(list(self._dict.keys()))

    @final
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
            If the key's value does not exist, use this value, unless it is None.

        Returns
        -------
        An instance of the specified validator
        """
        if key not in self._dict and default is None:
            raise self._validation_exception(f"{key} is missing when it should be present.")

        validator_name = f"{self._name}.{key}"
        validator_instance = validator(
            name=validator_name,
            value=self._dict.get(key, default),
        )

        self.__validator_dict[validator_name] = validator_instance
        return validator_instance

    @final
    def _validate_key_if_present(
        self,
        key: str,
        validator: Type[T],
        default: Optional[Any] = None,
    ) -> Optional[T]:
        """
        If the key does not exist in the dict, and no default is provided, return None.
        Otherwise, validate the key.

        Parameters
        ----------
        key
            Name of they key in the dict to validate
        validator
            The validator to use for the key's value
        default
            If the key's value does not exist, use this value.

        Returns
        -------
        An instance of the specified validator
        """
        if key not in self._dict and default is None:
            return None

        return self._validate_key(key=key, validator=validator, default=default)


class LiteralDictValidator(DictValidator):
    """DictValidator with exposed dict and keys method"""

    @property
    def dict(self) -> Dict:
        """Returns the entire dict"""
        return super()._dict

    @property
    def keys(self) -> List[str]:
        """Returns a sorted list of the dict's keys"""
        return super()._keys
