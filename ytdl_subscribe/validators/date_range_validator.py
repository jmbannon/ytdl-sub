from abc import ABC
from typing import Optional

from yt_dlp import DateRange

from ytdl_subscribe.validators.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.string_datetime import StringDatetimeValidator


class DateRangeValidator(StrictDictValidator, ABC):
    optional_keys = {"before", "after"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self.before = self._validate_key_if_present("before", StringDatetimeValidator)
        self.after = self._validate_key_if_present("after", StringDatetimeValidator)

    def get_date_range(self) -> Optional[DateRange]:
        if self.before or self.after:
            return DateRange(
                start=self.after.datetime_str if self.after else None,
                end=self.before.datetime_str if self.before else None,
            )
        return None
