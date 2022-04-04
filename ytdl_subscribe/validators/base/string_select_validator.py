import re
from keyword import iskeyword
from typing import List
from typing import Set

from ytdl_subscribe.validators.base.validators import StringValidator


class StringSelectValidator(StringValidator):
    """
    Ensures strings have selected one of the discrete allowed values.
    """

    select_values: Set[str] = set()

    def __init__(self, name, format_string: str):
        super().__init__(name=name, value=format_string)

        if self.value not in self.select_values:
            raise self._validation_exception(
                f"Must be one of the following values: {', '.join(self.select_values)}"
            )
