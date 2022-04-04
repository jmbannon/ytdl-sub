from typing import Optional

from ytdl_subscribe.validators.base.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.base.string_formatter_validator import (
    StringFormatterValidator,
)
from ytdl_subscribe.validators.base.string_select_validator import StringSelectValidator


class ConvertThumbnailValidator(StringSelectValidator):
    select_values = {"jpeg"}


class OutputOptionsValidator(StrictDictValidator):
    required_keys = {"output_directory", "file_name"}
    optional_keys = {"convert_thumbnail", "thumbnail_name"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self.output_directory: StringFormatterValidator = self.validate_key(
            key="output_directory", validator=StringFormatterValidator
        )

        self.file_name: StringFormatterValidator = self.validate_key(
            key="file_name", validator=StringFormatterValidator
        )

        self.convert_thumbnail: Optional[str] = None
        if "convert_thumbnail" in self.dict:
            self.convert_thumbnail = self.validate_key(
                key="convert_thumbnail", validator=ConvertThumbnailValidator
            ).value

        self.thumbnail_name: Optional[StringFormatterValidator] = None
        if "thumbnail_name" in self.dict:
            self.thumbnail_name = self.validate_key(
                key="thumbnail_name", validator=StringFormatterValidator
            )
