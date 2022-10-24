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

ValueT = TypeVar("ValueT", bound=object)
ValidationExceptionT = TypeVar("ValidationExceptionT", bound=ValidationException)
ValidatorT = TypeVar("ValidatorT", bound="Validator")


def validation_exception(
    name: str,
    error_message: str | Exception,
    exception_class: Type[ValidationExceptionT] = ValidationException,
) -> ValidationExceptionT:
    """
    Parameters
    ----------
    name
        Name of the validator
    error_message
        Error message to include in the ValidationException
    exception_class
        Class of the exception

    Returns
    -------
    Validation exception with a consistent prefix.
    """
    prefix = f"Validation error in {name}: "
    return exception_class(f"{prefix}{error_message}")


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

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Parameters
        ----------
        name
            Name of the validator
        value
            Value of the validator
        """
        _ = cls(name=name, value=value)

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
        self,
        error_message: str | Exception,
        exception_class: Type[ValidationExceptionT] = ValidationException,
    ) -> ValidationExceptionT:
        """
        Parameters
        ----------
        error_message
            Error message to include in the ValidationException

        Returns
        -------
        Validation exception with a consistent prefix.
        """
        return validation_exception(self._name, error_message, exception_class)


class ValueValidator(Validator, ABC, Generic[ValueT]):
    """
    Native type validator that returns the value as-is
    """

    @property
    def value(self) -> ValueT:
        """
        Returns
        -------
        The value, unmodified
        """
        return self._value


class BoolValidator(ValueValidator[bool]):
    _expected_value_type: Type = bool
    _expected_value_type_name = "boolean"


class StringValidator(ValueValidator[str]):
    _expected_value_type = str
    _expected_value_type_name = "string"


class FloatValidator(ValueValidator[float]):
    _expected_value_type = (int, float)
    _expected_value_type_name = "float"


class ListValidator(Validator, ABC, Generic[ValidatorT]):
    """
    Validates a list of objects to validate
    """

    _expected_value_type = list
    _expected_value_type_name = "list"

    _inner_list_type: Type[ValidatorT]

    def __init__(self, name, value):
        # If the value isn't actually a list, but a single value with the same type as the
        # _inner_list_type, cast it to a list with a single element
        if isinstance(value, self._inner_list_type._expected_value_type):
            value = [value]

        super().__init__(name, value)
        self._list: List[ValidatorT] = [
            self._inner_list_type(name=f"{name}.{i+1}", value=val)
            for i, val in enumerate(self._value)
        ]

    @property
    def list(self) -> List[ValidatorT]:
        """
        Returns
        -------
        The list
        """
        return self._list


class StringListValidator(ListValidator[StringValidator]):
    _expected_value_type_name = "string list"
    _inner_list_type = StringValidator


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
        validator: Type[ValidatorT],
        default: Optional[Any] = None,
    ) -> ValidatorT:
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
        validator: Type[ValidatorT],
        default: Optional[Any] = None,
    ) -> Optional[ValidatorT]:
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

    @final
    @classmethod
    def _partial_validate_key(
        cls, name: str, value: Any, key: str, validator: Type[ValidatorT]
    ) -> None:
        value_dict = DictValidator(name=name, value=value)
        if key in value_dict._dict:
            validator.partial_validate(name=f"{name}.{key}", value=value_dict._dict[key])


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
