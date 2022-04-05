import sanitize_filename

from ytdl_subscribe.validators.base.string_formatter_validator import (
    DictFormatterValidator,
)


class OverridesValidator(DictFormatterValidator):
    """Ensures `overrides` is a dict"""

    def __init__(self, name, value):
        super().__init__(name, value)
        for key in self._keys:
            self._value[f"sanitized_{key}"] = sanitize_filename.sanitize(
                self._value[key]
            )
