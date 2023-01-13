from datetime import datetime
from typing import Union

from yt_dlp.utils import sanitize_filename

from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.base_entry import BaseEntryVariables
from ytdl_sub.entries.variables.kwargs import CHANNEL
from ytdl_sub.entries.variables.kwargs import DOWNLOAD_INDEX
from ytdl_sub.entries.variables.kwargs import EXT
from ytdl_sub.entries.variables.kwargs import PLAYLIST_COUNT
from ytdl_sub.entries.variables.kwargs import PLAYLIST_DESCRIPTION
from ytdl_sub.entries.variables.kwargs import PLAYLIST_INDEX
from ytdl_sub.entries.variables.kwargs import PLAYLIST_MAX_UPLOAD_YEAR
from ytdl_sub.entries.variables.kwargs import PLAYLIST_MAX_UPLOAD_YEAR_TRUNCATED
from ytdl_sub.entries.variables.kwargs import PLAYLIST_TITLE
from ytdl_sub.entries.variables.kwargs import PLAYLIST_UID
from ytdl_sub.entries.variables.kwargs import PLAYLIST_UPLOADER
from ytdl_sub.entries.variables.kwargs import PLAYLIST_UPLOADER_ID
from ytdl_sub.entries.variables.kwargs import PLAYLIST_UPLOADER_URL
from ytdl_sub.entries.variables.kwargs import PLAYLIST_WEBPAGE_URL
from ytdl_sub.entries.variables.kwargs import SOURCE_COUNT
from ytdl_sub.entries.variables.kwargs import SOURCE_DESCRIPTION
from ytdl_sub.entries.variables.kwargs import SOURCE_INDEX
from ytdl_sub.entries.variables.kwargs import SOURCE_TITLE
from ytdl_sub.entries.variables.kwargs import SOURCE_UID
from ytdl_sub.entries.variables.kwargs import SOURCE_UPLOADER
from ytdl_sub.entries.variables.kwargs import SOURCE_UPLOADER_ID
from ytdl_sub.entries.variables.kwargs import SOURCE_UPLOADER_URL
from ytdl_sub.entries.variables.kwargs import SOURCE_WEBPAGE_URL
from ytdl_sub.entries.variables.kwargs import UPLOAD_DATE
from ytdl_sub.entries.variables.kwargs import UPLOAD_DATE_INDEX

# This file contains mixins to a BaseEntry subclass. Ignore pylint's "no kwargs member" suggestion
# pylint: disable=no-member
# pylint: disable=too-many-public-methods


def pad(num: int, width: int = 2):
    """Pad integers"""
    return str(num).zfill(width)


_days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

Self = Union[BaseEntry, "EntryVariables"]


class EntryVariables(BaseEntryVariables):
    @property
    def source_title(self: Self) -> str:
        """
        Returns
        -------
        str
            Name of the source (i.e. channel with multiple playlists) if it exists, otherwise
            returns its playlist_title.
        """
        return self.kwargs_get(SOURCE_TITLE, self.playlist_title)

    @property
    def source_title_sanitized(self: Self) -> str:
        """
        Returns
        -------
        str
            The source title, sanitized
        """
        return sanitize_filename(self.source_title)

    @property
    def source_uid(self: Self) -> str:
        """
        Returns
        -------
        str
            The source unique id if it exists, otherwise returns the playlist unique ID.
        """
        return self.kwargs_get(SOURCE_UID, self.playlist_uid)

    @property
    def source_index(self: Self) -> int:
        """
        Returns
        -------
        int
            Source index if it exists, otherwise returns ``1``.

            It is recommended to not use this unless you know the source will never add new content
            (it is easy for this value to change).
        """
        return self.kwargs_get(SOURCE_INDEX, self.playlist_index)

    @property
    def source_index_padded(self: Self) -> str:
        """
        Returns
        -------
        int
            The source index, padded.
        """
        return pad(self.source_index, 2)

    @property
    def source_count(self: Self) -> int:
        """
        Returns
        -------
        int
            The source count if it exists, otherwise returns the playlist count.
        """
        return self.kwargs_get(SOURCE_COUNT, self.playlist_count)

    @property
    def source_webpage_url(self: Self) -> str:
        """
        Returns
        -------
        str
            The source webpage url if it exists, otherwise returns the playlist webpage url.
        """
        return self.kwargs_get(SOURCE_WEBPAGE_URL, self.playlist_webpage_url)

    @property
    def source_description(self: Self) -> str:
        """
        Returns
        -------
        str
            The source description if it exists, otherwise returns the playlist description.
        """
        return self.kwargs_get(SOURCE_DESCRIPTION, self.playlist_description)

    @property
    def playlist_uid(self: Self) -> str:
        """
        Returns
        -------
        str
            The playlist unique ID if it exists, otherwise return the entry unique ID.
        """
        return self.kwargs_get(PLAYLIST_UID, self.uid)

    @property
    def playlist_title(self: Self) -> str:
        """
        Returns
        -------
        str
            Name of its parent playlist/channel if it exists, otherwise returns its title.
        """
        return self.kwargs_get(PLAYLIST_TITLE, self.title)

    @property
    def playlist_title_sanitized(self: Self) -> str:
        """
        Returns
        -------
        str
            The playlist name, sanitized
        """
        return sanitize_filename(self.playlist_title)

    @property
    def playlist_index(self: Self) -> int:
        """
        Returns
        -------
        int
            Playlist index if it exists, otherwise returns ``1``.

            Note that for channels/playlists, any change (i.e. adding or removing a video) will make
            this value change. Use with caution.
        """
        return self.kwargs_get(PLAYLIST_INDEX, 1)

    @property
    def playlist_index_reversed(self: Self) -> int:
        """
        Returns
        -------
        int
            Playlist index reversed via ``playlist_count - playlist_index + 1``
        """
        return self.playlist_count - self.playlist_index + 1

    @property
    def playlist_index_padded(self: Self) -> str:
        """
        Returns
        -------
        str
            playlist_index padded two digits
        """
        return pad(self.playlist_index, width=2)

    @property
    def playlist_index_reversed_padded(self: Self) -> str:
        """
        Returns
        -------
        str
            playlist_index_reversed padded two digits
        """
        return pad(self.playlist_index_reversed, width=2)

    @property
    def playlist_index_padded6(self: Self) -> str:
        """
        Returns
        -------
        str
            playlist_index padded six digits.
        """
        return pad(self.playlist_index, width=6)

    @property
    def playlist_index_reversed_padded6(self: Self) -> str:
        """
        Returns
        -------
        str
            playlist_index_reversed padded six digits.
        """
        return pad(self.playlist_index_reversed, width=6)

    @property
    def playlist_count(self: Self) -> int:
        """
        Returns
        -------
        int
            Playlist count if it exists, otherwise returns ``1``.

            Note that for channels/playlists, any change (i.e. adding or removing a video) will make
            this value change. Use with caution.
        """
        return self.kwargs_get(PLAYLIST_COUNT, 1)

    @property
    def playlist_description(self: Self) -> str:
        """
        Returns
        -------
        str
            The playlist description if it exists, otherwise returns the entry's description.
        """
        return self.kwargs_get(PLAYLIST_DESCRIPTION, self.description)

    @property
    def playlist_webpage_url(self: Self) -> str:
        """
        Returns
        -------
        str
            The playlist webpage url if it exists. Otherwise, returns the entry webpage url.
        """
        return self.kwargs_get(PLAYLIST_WEBPAGE_URL, self.webpage_url)

    @property
    def playlist_max_upload_year(self: Self) -> int:
        """
        Returns
        -------
        int
            Max upload_year for all entries in this entry's playlist if it exists, otherwise returns
            ``upload_year``
        """
        # override in EntryParent
        return self.kwargs_get(PLAYLIST_MAX_UPLOAD_YEAR, self.upload_year)

    @property
    def playlist_max_upload_year_truncated(self: Self) -> int:
        """
        Returns
        -------
        int
            The max playlist truncated upload year for all entries in this entry's playlist if it
            exists, otherwise returns ``upload_year_truncated``.
        """
        return self.kwargs_get(PLAYLIST_MAX_UPLOAD_YEAR_TRUNCATED, self.upload_year_truncated)

    @property
    def playlist_uploader_id(self: Self) -> str:
        """
        Returns
        -------
        str
            The playlist uploader id if it exists, otherwise returns the entry uploader ID.
        """
        return self.kwargs_get(PLAYLIST_UPLOADER_ID, self.uploader_id)

    @property
    def playlist_uploader(self: Self) -> str:
        """
        Returns
        -------
        str
            The playlist uploader if it exists, otherwise return the entry uploader.
        """
        return self.kwargs_get(PLAYLIST_UPLOADER, self.uploader)

    @property
    def playlist_uploader_sanitized(self: Self) -> str:
        """
        Returns
        -------
        str
            The playlist uploader, sanitized.
        """
        return sanitize_filename(self.playlist_uploader)

    @property
    def playlist_uploader_url(self: Self) -> str:
        """
        Returns
        -------
        str
            The playlist uploader url if it exists, otherwise returns the playlist webpage_url.
        """
        return self.kwargs_get(PLAYLIST_UPLOADER_URL, self.playlist_webpage_url)

    @property
    def source_uploader_id(self: Self) -> str:
        """
        Returns
        -------
        str
            The source uploader id if it exists, otherwise returns the playlist_uploader_id
        """
        return self.kwargs_get(SOURCE_UPLOADER_ID, self.playlist_uploader_id)

    @property
    def source_uploader(self: Self) -> str:
        """
        Returns
        -------
        str
            The source uploader if it exists, otherwise return the playlist_uploader
        """
        return self.kwargs_get(SOURCE_UPLOADER, self.playlist_uploader)

    @property
    def source_uploader_url(self: Self) -> str:
        """
        Returns
        -------
        str
            The source uploader url if it exists, otherwise returns the source webpage_url.
        """
        return self.kwargs_get(SOURCE_UPLOADER_URL, self.source_webpage_url)

    @property
    def channel(self: Self) -> str:
        """
        Returns
        -------
        str
            The channel name if it exists, otherwise returns the uploader.
        """
        return self.kwargs_get(CHANNEL, self.uploader)

    @property
    def channel_sanitized(self: Self) -> str:
        """
        Returns
        -------
        str
            The channel name, sanitized.
        """
        return sanitize_filename(self.channel)

    @property
    def ext(self: Self) -> str:
        """
        Returns
        -------
        str
            The downloaded entry's file extension
        """
        return self.kwargs(EXT)

    @property
    def thumbnail_ext(self: Self) -> str:
        """
        Returns
        -------
        str
            The download entry's thumbnail extension. Will always return 'jpg'. Until there is a
            need to support other image types, we always convert to jpg.
        """
        return "jpg"

    @property
    def download_index(self: Self) -> int:
        """
        Returns
        -------
        int
            The i'th entry downloaded. NOTE that this is fetched dynamically from the download
            archive.
        """
        return self.kwargs_get(DOWNLOAD_INDEX, 0) + 1

    @property
    def download_index_padded6(self: Self) -> str:
        """
        Returns
        -------
        str
            The download_index padded six digits
        """
        return pad(self.download_index, 6)

    @property
    def upload_date_index(self: Self) -> int:
        """
        Returns
        -------
        int
            The i'th entry downloaded with this upload date.
        """
        return self.kwargs_get(UPLOAD_DATE_INDEX, 0) + 1

    @property
    def upload_date_index_padded(self: Self) -> str:
        """
        Returns
        -------
        int
            The upload_date_index padded two digits
        """
        return pad(self.upload_date_index, 2)

    @property
    def upload_date_index_reversed(self: Self) -> int:
        """
        Returns
        -------
        int
            100 - upload_date_index
        """
        return 100 - self.upload_date_index

    @property
    def upload_date_index_reversed_padded(self: Self) -> str:
        """
        Returns
        -------
        int
            The upload_date_index padded two digits
        """
        return pad(self.upload_date_index_reversed, 2)

    @property
    def upload_date(self: Self) -> str:
        """
        Returns
        -------
        str
            The entry's uploaded date, in YYYYMMDD format. If not present, return today's date.
        """
        return self.kwargs_get(UPLOAD_DATE, datetime.now().strftime("%Y%m%d"))

    @property
    def upload_year(self: Self) -> int:
        """
        Returns
        -------
        int
            The entry's upload year
        """
        return int(self.upload_date[:4])

    @property
    def upload_year_truncated(self: Self) -> int:
        """
        Returns
        -------
        int
            The last two digits of the upload year, i.e. 22 in 2022
        """
        return int(str(self.upload_year)[-2:])

    @property
    def upload_year_truncated_reversed(self: Self) -> int:
        """
        Returns
        -------
        int
            The upload year truncated, but reversed using ``100 - {upload_year_truncated}``, i.e.
            2022 returns ``100 - 22`` = ``78``
        """
        return 100 - self.upload_year_truncated

    @property
    def upload_month_reversed(self: Self) -> int:
        """
        Returns
        -------
        int
            The upload month, but reversed using ``13 - {upload_month}``, i.e. March returns ``10``
        """
        return 13 - self.upload_month

    @property
    def upload_month_reversed_padded(self: Self) -> str:
        """
        Returns
        -------
        str
            The reversed upload month, but padded. i.e. November returns "02"
        """
        return pad(self.upload_month_reversed)

    @property
    def upload_month_padded(self: Self) -> str:
        """
        Returns
        -------
        str
            The entry's upload month padded to two digits, i.e. March returns "03"
        """
        return self.upload_date[4:6]

    @property
    def upload_day_padded(self: Self) -> str:
        """
        Returns
        -------
        str
            The entry's upload day padded to two digits, i.e. the fifth returns "05"
        """
        return self.upload_date[6:8]

    @property
    def upload_month(self: Self) -> int:
        """
        Returns
        -------
        int
            The upload month as an integer (no padding).
        """
        return int(self.upload_month_padded.lstrip("0"))

    @property
    def upload_day(self: Self) -> int:
        """
        Returns
        -------
        int
            The upload day as an integer (no padding).
        """
        return int(self.upload_day_padded.lstrip("0"))

    @property
    def upload_day_reversed(self: Self) -> int:
        """
        Returns
        -------
        int
            The upload day, but reversed using ``{total_days_in_month} + 1 - {upload_day}``,
            i.e. August 8th would have upload_day_reversed of ``31 + 1 - 8`` = ``24``
        """
        total_days_in_month = _days_in_month[self.upload_month]
        if self.upload_month == 2 and self.upload_year % 4 == 0:  # leap year
            total_days_in_month += 1

        return total_days_in_month + 1 - self.upload_day

    @property
    def upload_day_reversed_padded(self: Self) -> str:
        """
        Returns
        -------
        str
            The reversed upload day, but padded. i.e. August 30th returns "02".
        """
        return pad(self.upload_day_reversed)

    @property
    def upload_day_of_year(self: Self) -> int:
        """
        Returns
        -------
        int
            The day of the year, i.e. February 1st returns ``32``
        """
        output = sum(_days_in_month[: self.upload_month]) + self.upload_day
        if self.upload_month > 2 and self.upload_year % 4 == 0:
            output += 1

        return output

    @property
    def upload_day_of_year_padded(self: Self) -> str:
        """
        Returns
        -------
        str
            The upload day of year, but padded i.e. February 1st returns "032"
        """
        return pad(self.upload_day_of_year, width=3)

    @property
    def upload_day_of_year_reversed(self: Self) -> int:
        """
        Returns
        -------
        int
            The upload day, but reversed using ``{total_days_in_year} + 1 - {upload_day}``,
            i.e. February 2nd would have upload_day_of_year_reversed of ``365 + 1 - 32`` = ``334``
        """
        total_days_in_year = 365
        if self.upload_year % 4 == 0:
            total_days_in_year += 1

        return total_days_in_year + 1 - self.upload_day_of_year

    @property
    def upload_day_of_year_reversed_padded(self: Self) -> str:
        """
        Returns
        -------
        str
            The reversed upload day of year, but padded i.e. December 31st returns "001"
        """
        return pad(self.upload_day_of_year_reversed, width=3)

    @property
    def upload_date_standardized(self: Self) -> str:
        """
        Returns
        -------
        str
            The uploaded date formatted as YYYY-MM-DD
        """
        return f"{self.upload_year}-{self.upload_month_padded}-{self.upload_day_padded}"
