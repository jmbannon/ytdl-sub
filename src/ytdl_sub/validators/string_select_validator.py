from typing import Set

from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.validators import StringValidator


class StringSelectValidator(StringValidator):
    """
    Ensures strings have selected one of the discrete allowed values.
    """

    _select_values: Set[str] = set()

    def __init__(self, name, value: str):
        super().__init__(name=name, value=value)

        if self.value not in self._select_values:
            raise self._validation_exception(
                f"Must be one of the following values: {', '.join(self._select_values)}"
            )


class OverridesStringSelectValidator(OverridesStringFormatterValidator):
    _expected_value_type_name = "overrides select"

    _select_values: Set[str] = set()

    def post_process(self, resolved: str) -> str:
        if resolved not in self._select_values:
            raise self._validation_exception(
                f"Must be one of the following values: {', '.join(sorted(self._select_values))}"
            )

        return resolved
