from typing import Set

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
