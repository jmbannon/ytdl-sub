from typing import Dict
from typing import List
from typing import final

from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.base_entry import BaseEntry

# This file contains mixins to a BaseEntry subclass. Ignore pylint's "no kwargs member" suggestion
# pylint: disable=no-member


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
        The entry's unique ID
        """
        return self.kwargs("id")

    @property
    def extractor(self: BaseEntry) -> str:
        """
        Returns
        -------
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
        The title of the entry
        """
        return self.kwargs("title")

    @property
    def title_sanitized(self) -> str:
        """
        Returns
        -------
        The sanitized title of the entry, which is safe to use for Unix and Windows file names.
        """
        return sanitize_filename(self.title)

    @property
    def ext(self: BaseEntry) -> str:
        """
        Returns
        -------
        The downloaded entry's file extension
        """
        return self.kwargs("ext")

    @property
    def thumbnail_ext(self: BaseEntry) -> str:
        """
        Returns
        -------
        The download entry's thumbnail extension. Will always return 'jpg'. Until there is a need
        to support other image types, we always convert to jpg.
        """
        return "jpg"

    @property
    def upload_date(self: BaseEntry) -> str:
        """
        Returns
        -------
        The entry's uploaded date, in YYYYMMDD format.
        """
        return self.kwargs("upload_date")

    @property
    def upload_year(self) -> int:
        """
        Returns
        -------
        The entry's upload year
        """
        return int(self.upload_date[:4])

    @property
    def upload_year_truncated(self) -> int:
        """
        Returns
        -------
        The last two digits of the upload year, i.e. 22 in 2022
        """
        return int(self.upload_date[:2])

    @property
    def upload_month_padded(self) -> str:
        """
        Returns
        -------
        The entry's upload month padded to two digits, i.e. March returns "03"
        """
        return self.upload_date[4:6]

    @property
    def upload_day_padded(self) -> str:
        """
        Returns
        -------
        The entry's upload day padded to two digits, i.e. the fifth returns "05"
        """
        return self.upload_date[6:8]

    @property
    def upload_month(self) -> int:
        """
        Returns
        -------
        The upload month as an integer (no padding).
        """
        return int(self.upload_month_padded.lstrip("0"))

    @property
    def upload_day(self) -> int:
        """
        Returns
        -------
        The upload day as an integer (no padding).
        """
        return int(self.upload_day_padded.lstrip("0"))

    @property
    def upload_date_standardized(self) -> str:
        """
        Returns
        -------
        The uploaded date formatted as YYYY-MM-DD
        """
        return f"{self.upload_year}-{self.upload_month_padded}-{self.upload_day_padded}"

    @property
    def description(self: BaseEntry) -> str:
        """
        Returns
        -------
        The description of the entry.
        """
        return self.kwargs("description")
