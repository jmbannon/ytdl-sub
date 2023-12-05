from dataclasses import dataclass
from typing import Optional

# This file contains mixins to a BaseEntry subclass. Ignore pylint's "no kwargs member" suggestion
# pylint: disable=no-member
# pylint: disable=too-many-public-methods


@dataclass(frozen=True)
class KwargKey:
    entry_key: str
    variable_name: str

    @classmethod
    def init(cls, entry_key: str, variable_name: Optional[str] = None) -> "KwargKey":
        return cls(entry_key=entry_key, variable_name=variable_name if variable_name else entry_key)


class Variables:
    @property
    def uid(self) -> KwargKey:
        """
        Returns
        -------
        str
            The entry's unique ID
        """
        return KwargKey.init(entry_key="id", variable_name="uid")

    @property
    def uid_sanitized(self) -> KwargKey:
        """
        Returns
        -------
        str
            The sanitized uid of the entry, which is safe to use for Unix and Windows file names.
        """
        return KwargKey.init("uid_sanitized")

    @property
    def uid_sanitized_plex(self) -> KwargKey:
        """
        Returns
        -------
        str
            The sanitized uid with additional sanitizing for Plex. Replaces numbers with
            fixed-width numbers so Plex does not recognize them as season or episode numbers.
        """
        return KwargKey.init("uid_sanitized_plex")

    @property
    def ie_key(self) -> KwargKey:
        """
        Returns
        -------
        str
            The info-extractor key
        """
        return KwargKey.init("ie_key")

    @property
    def extractor(self) -> KwargKey:
        """
        Returns
        -------
        str
            The ytdl extractor name
        """
        return KwargKey.init("extractor")

    @property
    def epoch(self) -> KwargKey:
        """
        Returns
        -------
        int
            The unix epoch of when the metadata was scraped by yt-dlp.
        """
        return KwargKey.init("epoch")

    @property
    def epoch_date(self) -> KwargKey:
        """
        Returns
        -------
        str
            The epoch's date, in YYYYMMDD format.
        """
        return KwargKey.init("epoch_date")

    @property
    def epoch_hour(self) -> KwargKey:
        """
        Returns
        -------
        str
            The epoch's hour, padded
        """
        return KwargKey.init("epoch_hour")

    @property
    def title(self) -> KwargKey:
        """
        Returns
        -------
        str
            The title of the entry. If a title does not exist, returns its unique ID.
        """
        return KwargKey.init("title")

    @property
    def title_sanitized(self) -> KwargKey:
        """
        Returns
        -------
        str
            The sanitized title of the entry, which is safe to use for Unix and Windows file names.
        """
        return KwargKey.init("title_sanitized")

    @property
    def title_sanitized_plex(self) -> KwargKey:
        """
        Returns
        -------
        str
            The sanitized title with additional sanitizing for Plex. Replaces numbers with
            fixed-width numbers so Plex does not recognize them as season or episode numbers.
        """
        return KwargKey.init("title_sanitized_plex")

    @property
    def webpage_url(self) -> KwargKey:
        """
        Returns
        -------
        str
            The url to the webpage.
        """
        return KwargKey.init("webpage_url")

    @property
    def info_json_ext(self) -> KwargKey:
        """
        Returns
        -------
        str
            The "info.json" extension
        """
        return KwargKey.init("info_json_ext")

    @property
    def description(self) -> KwargKey:
        """
        Returns
        -------
        str
            The description if it exists. Otherwise, returns an emtpy string.
        """
        return KwargKey.init("description")

    @property
    def uploader_id(self) -> KwargKey:
        """
        Returns
        -------
        str
            The uploader id if it exists, otherwise return the unique ID.
        """
        return KwargKey.init("uploader_id")

    @property
    def uploader(self) -> KwargKey:
        """
        Returns
        -------
        str
            The uploader if it exists, otherwise return the uploader ID.
        """
        return KwargKey.init("uploader")

    @property
    def uploader_url(self) -> KwargKey:
        """
        Returns
        -------
        str
            The uploader url if it exists, otherwise returns the webpage_url.
        """
        return KwargKey.init("uploader_url")

    @property
    def source_title(self) -> KwargKey:
        """
        Returns
        -------
        str
            Name of the source (i.e. channel with multiple playlists) if it exists, otherwise
            returns its playlist_title.
        """
        return KwargKey.init("source_title")

    @property
    def source_title_sanitized(self) -> KwargKey:
        """
        Returns
        -------
        str
            The source title, sanitized
        """
        return KwargKey.init("source_title_sanitized")

    @property
    def source_uid(self) -> KwargKey:
        """
        Returns
        -------
        str
            The source unique id if it exists, otherwise returns the playlist unique ID.
        """
        return KwargKey.init("source_uid")

    @property
    def source_index(self) -> KwargKey:
        """
        Returns
        -------
        int
            Source index if it exists, otherwise returns ``1``.

            It is recommended to not use this unless you know the source will never add new content
            (it is easy for this value to change).
        """
        return KwargKey.init("source_index")

    @property
    def source_index_padded(self) -> KwargKey:
        """
        Returns
        -------
        int
            The source index, padded.
        """
        return KwargKey.init("source_index_padded")

    @property
    def source_count(self) -> KwargKey:
        """
        Returns
        -------
        int
            The source count if it exists, otherwise returns the playlist count.
        """
        return KwargKey.init("source_count")

    @property
    def source_webpage_url(self) -> KwargKey:
        """
        Returns
        -------
        str
            The source webpage url if it exists, otherwise returns the playlist webpage url.
        """
        return KwargKey.init("source_webpage_url")

    @property
    def source_description(self) -> KwargKey:
        """
        Returns
        -------
        str
            The source description if it exists, otherwise returns the playlist description.
        """
        return KwargKey.init("source_description")

    @property
    def playlist_uid(self) -> KwargKey:
        """
        Returns
        -------
        str
            The playlist unique ID if it exists, otherwise return KwargKey.init("")
        """
        return KwargKey.init("playlist_uid")

    @property
    def playlist_title(self) -> KwargKey:
        """
        Returns
        -------
        str
            Name of its parent playlist/channel if it exists, otherwise returns its title.
        """
        return KwargKey.init("playlist_title")

    @property
    def playlist_title_sanitized(self) -> KwargKey:
        """
        Returns
        -------
        str
            The playlist name, sanitized
        """
        return KwargKey.init("playlist_title_sanitized")

    @property
    def playlist_index(self) -> KwargKey:
        """
        Returns
        -------
        int
            Playlist index if it exists, otherwise returns ``1``.

            Note that for channels/playlists, any change (i.e. adding or removing a video) will make
            this value change. Use with caution.
        """
        return KwargKey.init("playlist_index")

    @property
    def playlist_index_reversed(self) -> KwargKey:
        """
        Returns
        -------
        int
            Playlist index reversed via ``playlist_count - playlist_index + 1``
        """
        return KwargKey.init("playlist_index_reversed")

    @property
    def playlist_index_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            playlist_index padded two digits
        """
        return KwargKey.init("playlist_index_padded")

    @property
    def playlist_index_reversed_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            playlist_index_reversed padded two digits
        """
        return KwargKey.init("playlist_index_reversed_padded")

    @property
    def playlist_index_padded6(self) -> KwargKey:
        """
        Returns
        -------
        str
            playlist_index padded six digits.
        """
        return KwargKey.init("playlist_index_padded6")

    @property
    def playlist_index_reversed_padded6(self) -> KwargKey:
        """
        Returns
        -------
        str
            playlist_index_reversed padded six digits.
        """
        return KwargKey.init("playlist_index_reversed_padded6")

    @property
    def playlist_count(self) -> KwargKey:
        """
        Returns
        -------
        int
            Playlist count if it exists, otherwise returns ``1``.

            Note that for channels/playlists, any change (i.e. adding or removing a video) will make
            this value change. Use with caution.
        """
        return KwargKey.init("playlist_count")

    @property
    def playlist_description(self) -> KwargKey:
        """
        Returns
        -------
        str
            The playlist description if it exists, otherwise returns the entry's description.
        """
        return KwargKey.init("playlist_description")

    @property
    def playlist_webpage_url(self) -> KwargKey:
        """
        Returns
        -------
        str
            The playlist webpage url if it exists. Otherwise, returns the entry webpage url.
        """
        return KwargKey.init("playlist_webpage_url")

    @property
    def playlist_max_upload_year(self) -> KwargKey:
        """
        Returns
        -------
        int
            Max upload_year for all entries in this entry's playlist if it exists, otherwise returns
            ``upload_year``
        """
        # override in EntryParent
        return KwargKey.init("playlist_max_upload_year")

    @property
    def playlist_max_upload_year_truncated(self) -> KwargKey:
        """
        Returns
        -------
        int
            The max playlist truncated upload year for all entries in this entry's playlist if it
            exists, otherwise returns ``upload_year_truncated``.
        """
        return KwargKey.init("playlist_max_upload_year_truncated")

    @property
    def playlist_uploader_id(self) -> KwargKey:
        """
        Returns
        -------
        str
            The playlist uploader id if it exists, otherwise returns the entry uploader ID.
        """
        return KwargKey.init("playlist_uploader_id")

    @property
    def playlist_uploader(self) -> KwargKey:
        """
        Returns
        -------
        str
            The playlist uploader if it exists, otherwise return KwargKey.init("")
        """
        return KwargKey.init("playlist_uploader")

    @property
    def playlist_uploader_sanitized(self) -> KwargKey:
        """
        Returns
        -------
        str
            The playlist uploader, sanitized.
        """
        return KwargKey.init("playlist_uploader_sanitized")

    @property
    def playlist_uploader_url(self) -> KwargKey:
        """
        Returns
        -------
        str
            The playlist uploader url if it exists, otherwise returns the playlist webpage_url.
        """
        return KwargKey.init("playlist_uploader_url")

    @property
    def source_uploader_id(self) -> KwargKey:
        """
        Returns
        -------
        str
            The source uploader id if it exists, otherwise returns the playlist_uploader_id
        """
        return KwargKey.init("source_uploader_id")

    @property
    def source_uploader(self) -> KwargKey:
        """
        Returns
        -------
        str
            The source uploader if it exists, otherwise return KwargKey.init("")
        """
        return KwargKey.init("source_uploader")

    @property
    def source_uploader_url(self) -> KwargKey:
        """
        Returns
        -------
        str
            The source uploader url if it exists, otherwise returns the source webpage_url.
        """
        return KwargKey.init("source_uploader_url")

    @property
    def creator(self) -> KwargKey:
        """
        Returns
        -------
        str
            The creator name if it exists, otherwise returns the channel.
        """
        return KwargKey.init("creator")

    @property
    def creator_sanitized(self) -> KwargKey:
        """
        Returns
        -------
        str
            The creator name, sanitized
        """
        return KwargKey.init("creator_sanitized")

    @property
    def channel(self) -> KwargKey:
        """
        Returns
        -------
        str
            The channel name if it exists, otherwise returns the uploader.
        """
        return KwargKey.init("channel")

    @property
    def channel_sanitized(self) -> KwargKey:
        """
        Returns
        -------
        str
            The channel name, sanitized.
        """
        return KwargKey.init("channel_sanitized")

    @property
    def channel_id(self) -> KwargKey:
        """
        Returns
        -------
        str
            The channel id if it exists, otherwise returns the entry uploader ID.
        """
        return KwargKey.init("channel_id")

    @property
    def ext(self) -> KwargKey:
        """
        Returns
        -------
        str
            The downloaded entry's file extension
        """
        return KwargKey.init("ext")

    @property
    def thumbnail_ext(self) -> KwargKey:
        """
        Returns
        -------
        str
            The download entry's thumbnail extension. Will always return KwargKey.init("")
            need to support other image types, we always convert to jpg.
        """
        return KwargKey.init("thumbnail_ext")

    @property
    def download_index(self) -> KwargKey:
        """
        Returns
        -------
        int
            The i'th entry downloaded. NOTE that this is fetched dynamically from the download
            archive.
        """
        return KwargKey.init("download_index")

    @property
    def download_index_padded6(self) -> KwargKey:
        """
        Returns
        -------
        str
            The download_index padded six digits
        """
        return KwargKey.init("download_index_padded6")

    @property
    def upload_date_index(self) -> KwargKey:
        """
        Returns
        -------
        int
            The i'th entry downloaded with this upload date.
        """
        return KwargKey.init("upload_date_index")

    @property
    def upload_date_index_padded(self) -> KwargKey:
        """
        Returns
        -------
        int
            The upload_date_index padded two digits
        """
        return KwargKey.init("upload_date_index_padded")

    @property
    def upload_date_index_reversed(self) -> KwargKey:
        """
        Returns
        -------
        int
            100 - upload_date_index
        """
        return KwargKey.init("upload_date_index_reversed")

    @property
    def upload_date_index_reversed_padded(self) -> KwargKey:
        """
        Returns
        -------
        int
            The upload_date_index padded two digits
        """
        return KwargKey.init("upload_date_index_reversed_padded")

    @property
    def upload_date(self) -> KwargKey:
        """
        Returns
        -------
        str
            The entry's uploaded date, in YYYYMMDD format. If not present, return KwargKey.init("")
        """
        return KwargKey.init("upload_date")

    @property
    def upload_year(self) -> KwargKey:
        """
        Returns
        -------
        int
            The entry's upload year
        """
        return KwargKey.init("upload_year")

    @property
    def upload_year_truncated(self) -> KwargKey:
        """
        Returns
        -------
        int
            The last two digits of the upload year, i.e. 22 in 2022
        """
        return KwargKey.init("upload_year_truncated")

    @property
    def upload_year_truncated_reversed(self) -> KwargKey:
        """
        Returns
        -------
        int
            The upload year truncated, but reversed using ``100 - {upload_year_truncated}``, i.e.
            2022 returns ``100 - 22`` = ``78``
        """
        return KwargKey.init("upload_year_truncated_reversed")

    @property
    def upload_month_reversed(self) -> KwargKey:
        """
        Returns
        -------
        int
            The upload month, but reversed using ``13 - {upload_month}``, i.e. March returns ``10``
        """
        return KwargKey.init("upload_month_reversed")

    @property
    def upload_month_reversed_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The reversed upload month, but padded. i.e. November returns "02"
        """
        return KwargKey.init("upload_month_reversed_padded")

    @property
    def upload_month_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The entry's upload month padded to two digits, i.e. March returns "03"
        """
        return KwargKey.init("upload_month_padded")

    @property
    def upload_day_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The entry's upload day padded to two digits, i.e. the fifth returns "05"
        """
        return KwargKey.init("upload_day_padded")

    @property
    def upload_month(self) -> KwargKey:
        """
        Returns
        -------
        int
            The upload month as an integer (no padding).
        """
        return KwargKey.init("upload_month")

    @property
    def upload_day(self) -> KwargKey:
        """
        Returns
        -------
        int
            The upload day as an integer (no padding).
        """
        return KwargKey.init("upload_day")

    @property
    def upload_day_reversed(self) -> KwargKey:
        """
        Returns
        -------
        int
            The upload day, but reversed using ``{total_days_in_month} + 1 - {upload_day}``,
            i.e. August 8th would have upload_day_reversed of ``31 + 1 - 8`` = ``24``
        """
        return KwargKey.init("upload_day_reversed")

    @property
    def upload_day_reversed_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The reversed upload day, but padded. i.e. August 30th returns "02".
        """
        return KwargKey.init("upload_day_reversed_padded")

    @property
    def upload_day_of_year(self) -> KwargKey:
        """
        Returns
        -------
        int
            The day of the year, i.e. February 1st returns ``32``
        """
        return KwargKey.init("upload_day_of_year")

    @property
    def upload_day_of_year_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The upload day of year, but padded i.e. February 1st returns "032"
        """
        return KwargKey.init("upload_day_of_year_padded")

    @property
    def upload_day_of_year_reversed(self) -> KwargKey:
        """
        Returns
        -------
        int
            The upload day, but reversed using ``{total_days_in_year} + 1 - {upload_day}``,
            i.e. February 2nd would have upload_day_of_year_reversed of ``365 + 1 - 32`` = ``334``
        """
        return KwargKey.init("upload_day_of_year_reversed")

    @property
    def upload_day_of_year_reversed_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The reversed upload day of year, but padded i.e. December 31st returns "001"
        """
        return KwargKey.init("upload_day_of_year_reversed_padded")

    @property
    def upload_date_standardized(self) -> KwargKey:
        """
        Returns
        -------
        str
            The uploaded date formatted as YYYY-MM-DD
        """
        return KwargKey.init("upload_date_standardized")

    @property
    def release_date(self) -> KwargKey:
        """
        Returns
        -------
        str
            The entry's release date, in YYYYMMDD format. If not present, return KwargKey.init("")
        """
        return KwargKey.init("release_date")

    @property
    def release_year(self) -> KwargKey:
        """
        Returns
        -------
        int
            The entry's release year
        """
        return KwargKey.init("release_year")

    @property
    def release_year_truncated(self) -> KwargKey:
        """
        Returns
        -------
        int
            The last two digits of the release year, i.e. 22 in 2022
        """
        return KwargKey.init("release_year_truncated")

    @property
    def release_year_truncated_reversed(self) -> KwargKey:
        """
        Returns
        -------
        int
            The release year truncated, but reversed using ``100 - {release_year_truncated}``, i.e.
            2022 returns ``100 - 22`` = ``78``
        """
        return KwargKey.init("release_year_truncated_reversed")

    @property
    def release_month_reversed(self) -> KwargKey:
        """
        Returns
        -------
        int
            The release month, but reversed
            using ``13 - {release_month}``, i.e. March returns ``10``
        """
        return KwargKey.init("release_month_reversed")

    @property
    def release_month_reversed_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The reversed release month, but padded. i.e. November returns "02"
        """
        return KwargKey.init("release_month_reversed_padded")

    @property
    def release_month_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The entry's release month padded to two digits, i.e. March returns "03"
        """
        return KwargKey.init("release_month_padded")

    @property
    def release_day_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The entry's release day padded to two digits, i.e. the fifth returns "05"
        """
        return KwargKey.init("release_day_padded")

    @property
    def release_month(self) -> KwargKey:
        """
        Returns
        -------
        int
            The release month as an integer (no padding).
        """
        return KwargKey.init("release_month")

    @property
    def release_day(self) -> KwargKey:
        """
        Returns
        -------
        int
            The release day as an integer (no padding).
        """
        return KwargKey.init("release_day")

    @property
    def release_day_reversed(self) -> KwargKey:
        """
        Returns
        -------
        int
            The release day, but reversed using ``{total_days_in_month} + 1 - {release_day}``,
            i.e. August 8th would have release_day_reversed of ``31 + 1 - 8`` = ``24``
        """
        return KwargKey.init("release_day_reversed")

    @property
    def release_day_reversed_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The reversed release day, but padded. i.e. August 30th returns "02".
        """
        return KwargKey.init("release_day_reversed_padded")

    @property
    def release_day_of_year(self) -> KwargKey:
        """
        Returns
        -------
        int
            The day of the year, i.e. February 1st returns ``32``
        """
        return KwargKey.init("release_day_of_year")

    @property
    def release_day_of_year_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The release day of year, but padded i.e. February 1st returns "032"
        """
        return KwargKey.init("release_day_of_year_padded")

    @property
    def release_day_of_year_reversed(self) -> KwargKey:
        """
        Returns
        -------
        int
            The release day, but reversed using ``{total_days_in_year} + 1 - {release_day}``,
            i.e. February 2nd would have release_day_of_year_reversed of ``365 + 1 - 32`` = ``334``
        """
        return KwargKey.init("release_day_of_year_reversed")

    @property
    def release_day_of_year_reversed_padded(self) -> KwargKey:
        """
        Returns
        -------
        str
            The reversed release day of year, but padded i.e. December 31st returns "001"
        """
        return KwargKey.init("release_day_of_year_reversed_padded")

    @property
    def release_date_standardized(self) -> KwargKey:
        """
        Returns
        -------
        str
            The release date formatted as YYYY-MM-DD
        """
        return KwargKey.init("release_date_standardized")
