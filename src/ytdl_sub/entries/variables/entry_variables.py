from typing import Dict
from typing import List
from typing import final

from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.base_entry import BaseEntry

# This file contains mixins to a BaseEntry subclass. Ignore pylint's "no kwargs member" suggestion
# pylint: disable=no-member


def _pad(num):
    if num < 10:
        return f"0{num}"
    return str(num)


class SourceVariables:
    """
    Source variables are ``{variables}`` that contain metadata from downloaded media.
    These variables can be used with fields that expect
    :class:`~ytdl_sub.validators.string_formatter_validators.StringFormatterValidator`,
    but not
    :class:`~ytdl_sub.validators.string_formatter_validators.OverridesStringFormatterValidator`.
    """

    @property
    def uid(self: BaseEntry) -> str:
        """
        Returns
        -------
        str
            The entry's unique ID
        """
        return self.kwargs("id")

    @property
    def extractor(self: BaseEntry) -> str:
        """
        Returns
        -------
        str
            The ytdl extractor name
        """
        return self.kwargs("extractor")

    def _added_variables(self: BaseEntry) -> Dict[str, str]:
        """
        Returns
        -------
        Dict of variables added to this entry
        """
        return self._additional_variables

    @classmethod
    def source_variables(cls) -> List[str]:
        """
        Returns
        -------
        List of all source variables
        """
        property_names = [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property)]
        return property_names

    @final
    def _to_dict(self) -> Dict[str, str]:
        """
        Returns
        -------
        Dictionary containing all variables
        """
        source_variable_dict = {
            source_var: getattr(self, source_var) for source_var in self.source_variables()
        }
        return dict(source_variable_dict, **self._added_variables())


class EntryVariables(SourceVariables):
    @property
    def title(self: BaseEntry) -> str:
        """
        Returns
        -------
        str
            The title of the entry
        """
        return self.kwargs("title")

    @property
    def title_sanitized(self) -> str:
        """
        Returns
        -------
        str
            The sanitized title of the entry, which is safe to use for Unix and Windows file names.
        """
        return sanitize_filename(self.title)

    @property
    def ext(self: BaseEntry) -> str:
        """
        Returns
        -------
        str
            The downloaded entry's file extension
        """
        return self.kwargs("ext")

    @property
    def thumbnail_ext(self: BaseEntry) -> str:
        """
        Returns
        -------
        str
            The download entry's thumbnail extension. Will always return 'jpg'. Until there is a
            need to support other image types, we always convert to jpg.
        """
        return "jpg"

    @property
    def upload_date(self: BaseEntry) -> str:
        """
        Returns
        -------
        str
            The entry's uploaded date, in YYYYMMDD format.
        """
        return self.kwargs("upload_date")

    @property
    def upload_year(self) -> int:
        """
        Returns
        -------
        int
            The entry's upload year
        """
        return int(self.upload_date[:4])

    @property
    def upload_year_truncated(self) -> int:
        """
        Returns
        -------
        int
            The last two digits of the upload year, i.e. 22 in 2022
        """
        return int(str(self.upload_year)[-2:])

    @property
    def upload_year_truncated_reversed(self) -> int:
        """
        Returns
        -------
        int
            The upload year truncated, but reversed using ``100 - {upload_year_truncated}``, i.e.
            2022 returns ``100 - 22`` = ``78``
        """
        return 100 - self.upload_year_truncated

    @property
    def upload_month_reversed(self) -> int:
        """
        Returns
        -------
        int
            The upload month, but reversed using ``13 - {upload_month}``, i.e. March returns ``10``
        """
        return 13 - self.upload_month

    @property
    def upload_month_reversed_padded(self) -> str:
        """
        Returns
        -------
        str
            The reversed upload month, but padded. i.e. November returns "02"
        """
        return _pad(self.upload_month_reversed)

    @property
    def upload_month_padded(self) -> str:
        """
        Returns
        -------
        str
            The entry's upload month padded to two digits, i.e. March returns "03"
        """
        return self.upload_date[4:6]

    @property
    def upload_day_padded(self) -> str:
        """
        Returns
        -------
        str
            The entry's upload day padded to two digits, i.e. the fifth returns "05"
        """
        return self.upload_date[6:8]

    @property
    def upload_month(self) -> int:
        """
        Returns
        -------
        int
            The upload month as an integer (no padding).
        """
        return int(self.upload_month_padded.lstrip("0"))

    @property
    def upload_day(self) -> int:
        """
        Returns
        -------
        int
            The upload day as an integer (no padding).
        """
        return int(self.upload_day_padded.lstrip("0"))

    @property
    def upload_day_reversed(self) -> int:
        """
        Returns
        -------
        int
            The upload day, but reversed using ``{total_days_in_month} + 1 - {upload_day}``,
            i.e. August 8th would have upload_day_reversed of ``31 + 1 - 8`` = ``24``
        """
        total_days_in_month: int = 30
        if self.upload_month in [1, 3, 5, 7, 8, 10, 12]:
            total_days_in_month = 31
        elif self.upload_month == 2:
            total_days_in_month = 28
            if self.upload_year % 4 == 0:  # leap year
                total_days_in_month = 29

        return total_days_in_month + 1 - self.upload_day

    @property
    def upload_day_reversed_padded(self) -> str:
        """
        Returns
        -------
        str
            The reversed upload day, but padded. i.e. August 30th returns "02".
        """
        return _pad(self.upload_day_reversed)

    @property
    def upload_date_standardized(self) -> str:
        """
        Returns
        -------
        str
            The uploaded date formatted as YYYY-MM-DD
        """
        return f"{self.upload_year}-{self.upload_month_padded}-{self.upload_day_padded}"
