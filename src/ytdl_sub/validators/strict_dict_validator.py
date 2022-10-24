from typing import List
from typing import Set

from ytdl_sub.validators.validators import DictValidator


class StrictDictValidator(DictValidator):
    """
    Validates dictionary-based fields with required and optional keys.
    """

    _required_keys: Set[str] = set()
    _optional_keys: Set[str] = set()
    _allow_extra_keys = False

    def __init__(self, name, value):
        super().__init__(name, value)

        if len(self._allowed_keys) == 0:
            raise ValueError(
                "No required or optional keys defined when using a StrictDictValidator. "
                "Should be using DictValidator instead."
            )

        # Ensure all required keys are present
        for required_key in self._required_keys:
            if required_key not in self._dict:
                raise self._validation_exception(f"missing the required field '{required_key}'")

        # Ensure all keys are either required or optional keys if no extra field are allowed
        if not self._allow_extra_keys:
            for object_key in self._keys:
                if object_key not in self._allowed_keys:
                    error_msg = (
                        f"'{self._name}' contains the field '{object_key}' which is not allowed. "
                        f"Allowed fields: {', '.join(self._allowed_keys)}"
                    )
                    raise self._validation_exception(str(error_msg))

    @property
    def _allowed_keys(self) -> List[str]:
        """
        Returns
        -------
        Sorted list of required and optional keys
        """
        return sorted(list(self._required_keys.union(self._optional_keys)))
