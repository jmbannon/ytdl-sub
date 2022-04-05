from typing import Optional

from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.string_formatter_validator import (
    StringFormatterValidator,
)
from ytdl_subscribe.validators.base.string_select_validator import StringSelectValidator


class ConvertThumbnailValidator(StringSelectValidator):
    _select_values = {"jpeg"}


class OutputOptionsValidator(StrictDictValidator):
    _required_keys = {"output_directory", "file_name"}
    _optional_keys = {"convert_thumbnail", "thumbnail_name"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self.output_directory: StringFormatterValidator = self._validate_key(
            key="output_directory", validator=StringFormatterValidator
        )
        self.file_name: StringFormatterValidator = self._validate_key(
            key="file_name", validator=StringFormatterValidator
        )

        self.convert_thumbnail = self._validate_key_if_present(
            key="convert_thumbnail", validator=ConvertThumbnailValidator
        )
        self.thumbnail_name = self._validate_key_if_present(
            key="thumbnail_name", validator=StringFormatterValidator
        )
