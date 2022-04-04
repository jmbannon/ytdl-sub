from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.string_formatter_validator import (
    DictFormatterValidator,
)
from ytdl_subscribe.validators.base.string_formatter_validator import (
    StringFormatterValidator,
)
from ytdl_subscribe.validators.base.string_select_validator import StringSelectValidator
from ytdl_subscribe.validators.base.validators import StringValidator


class NFOValidator(StrictDictValidator):
    required_keys = {"nfo_name", "nfo_root", "tags"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self.nfo_name = self.validate_key(
            key="nfo_name", validator=StringFormatterValidator
        )
        self.nfo_root = self.validate_key(
            key="nfo_root", validator=StringFormatterValidator
        )
        self.tags = self.validate_key(key="tags", validator=DictFormatterValidator)
