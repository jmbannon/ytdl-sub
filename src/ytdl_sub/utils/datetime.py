from typing import Optional

from yt_dlp import DateRange
from yt_dlp.utils import datetime_from_str

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.validators.string_datetime import StringDatetimeValidator


def to_date_range(
    before: Optional[StringDatetimeValidator],
    after: Optional[StringDatetimeValidator],
    overrides: Overrides,
) -> Optional[DateRange]:
    """
    Returns
    -------
    Date range if the 'before' or 'after' is defined. None otherwise.
    """
    start: Optional[str] = None
    end: Optional[str] = None

    if after:
        start = overrides.apply_formatter(formatter=after)

    if before:
        end = overrides.apply_formatter(formatter=before)

    if start or end:
        return DateRange(start=start, end=end)

    return None


def to_date_str(date_validator: StringDatetimeValidator, overrides: Overrides) -> str:
    """
    Returns
    -------
    Date in the form of YYYYMMDD as a string
    """
    date_str = overrides.apply_formatter(formatter=date_validator)
    return datetime_from_str(date_str).date().strftime("%Y%m%d")
