from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.string_formatter_validators import (
    DictFormatterValidator,
)
from ytdl_subscribe.validators.base.string_formatter_validators import (
    StringFormatterValidator,
)


class NFOValidator(StrictDictValidator):
    _required_keys = {"nfo_name", "nfo_root", "tags"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self.nfo_name = self._validate_key(
            key="nfo_name", validator=StringFormatterValidator
        )
        self.nfo_root = self._validate_key(
            key="nfo_root", validator=StringFormatterValidator
        )
        self.tags = self._validate_key(key="tags", validator=DictFormatterValidator)
