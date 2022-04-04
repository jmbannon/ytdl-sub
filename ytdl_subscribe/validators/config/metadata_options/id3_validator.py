from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.string_formatter_validator import (
    DictFormatterValidator,
)
from ytdl_subscribe.validators.base.string_select_validator import StringSelectValidator
from ytdl_subscribe.validators.base.validators import StringValidator


class Id3VersionValidator(StringSelectValidator):
    _select_values = {"2.3", "2.4"}


class Id3Validator(StrictDictValidator):
    _required_keys = {"id3_version", "tags"}
    _optional_keys = {"multi_value_separator"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self.id3_version = self.validate_key(
            key="id3_version", validator=Id3VersionValidator
        ).value
        self.tags = self.validate_key(key="tags", validator=DictFormatterValidator)

        self.multi_value_separator = self.validate_key_if_present(
            key="multi_value_separator", validator=StringValidator
        )
