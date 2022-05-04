from typing import Optional

from yt_dlp import DateRange

from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_datetime import StringDatetimeValidator


class DateRangeValidator(StrictDictValidator):
    _optional_keys = {"before", "after"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._before = self._validate_key_if_present("before", StringDatetimeValidator)
        self._after = self._validate_key_if_present("after", StringDatetimeValidator)

    @property
    def before(self) -> Optional[StringDatetimeValidator]:
        """Optional. Only download videos before this datetime."""
        return self._before

    @property
    def after(self) -> Optional[StringDatetimeValidator]:
        """Optional. Only download videos after this datetime."""
        return self._after

    def get_date_range(self) -> Optional[DateRange]:
        """
        Returns
        -------
        Date range if the 'before' or 'after' is defined. None otherwise.
        """
        if self._before or self._after:
            return DateRange(
                start=self._after.datetime_str if self._after else None,
                end=self._before.datetime_str if self._before else None,
            )
        return None
