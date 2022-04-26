from typing import Optional

from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.entry import Entry
from ytdl_sub.validators.date_range_validator import DateRangeValidator
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import BoolValidator
from ytdl_sub.validators.validators import LiteralDictValidator


class YTDLOptions(LiteralDictValidator):
    """Ensures `ytdl_options` is a dict"""


class Overrides(DictFormatterValidator):
    """Ensures `overrides` is a dict"""

    def __init__(self, name, value):
        super().__init__(name, value)
        for key in self._keys:
            sanitized_key_name = f"sanitized_{key}"
            # First, sanitize the format string
            self._value[sanitized_key_name] = sanitize_filename(self._value[key].format_string)

            # Then, convert it into a StringFormatterValidator
            self._value[sanitized_key_name] = StringFormatterValidator(
                name="__should_never_fail__",
                value=self._value[sanitized_key_name],
            )

    def apply_formatter(
        self, formatter: StringFormatterValidator, entry: Optional[Entry] = None
    ) -> str:
        """
        Returns the format_string after .format has been called on it using entry (if provided) and
        override values
        """
        variable_dict = self.dict_with_format_strings
        if entry:
            variable_dict = dict(entry.to_dict(), **variable_dict)
        return formatter.apply_formatter(variable_dict)


class OutputOptions(StrictDictValidator):
    """Where to output the final files and thumbnails"""

    _required_keys = {"output_directory", "file_name"}
    _optional_keys = {
        "thumbnail_name",
        "maintain_download_archive",
        "keep_files",
    }

    def __init__(self, name, value):
        super().__init__(name, value)

        # Output directory should resolve without any entry variables.
        # This is to check the directory for any download-archives before any downloads begin
        self.output_directory: OverridesStringFormatterValidator = self._validate_key(
            key="output_directory", validator=OverridesStringFormatterValidator
        )

        # file name and thumbnails however can use entry variables
        self.file_name: StringFormatterValidator = self._validate_key(
            key="file_name", validator=StringFormatterValidator
        )
        self.thumbnail_name = self._validate_key_if_present(
            key="thumbnail_name", validator=StringFormatterValidator
        )

        self.maintain_download_archive = self._validate_key_if_present(
            key="maintain_download_archive", validator=BoolValidator, default=False
        )
        self.delete_stale_files = self._validate_key_if_present(
            key="keep_files", validator=DateRangeValidator
        )

        if self.delete_stale_files and not self.maintain_download_archive:
            raise self._validation_exception(
                "keep_files requires maintain_download_archive set to True"
            )
