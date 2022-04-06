import sanitize_filename

from ytdl_subscribe.validators.base.string_formatter_validators import (
    DictFormatterValidator,
)
from ytdl_subscribe.validators.base.string_formatter_validators import (
    StringFormatterValidator,
)


class OverridesValidator(DictFormatterValidator):
    """Ensures `overrides` is a dict"""

    def __init__(self, name, value):
        super().__init__(name, value)
        for key in self._keys:
            sanitized_key_name = f"sanitized_{key}"
            # First, sanitize the format string
            self._value[sanitized_key_name] = sanitize_filename.sanitize(
                self._value[key].format_string
            )

            # Then, convert it into a StringFormatterValidator
            self._value[sanitized_key_name] = StringFormatterValidator(
                name="__should_never_fail__",
                value=self._value[sanitized_key_name],
            )
