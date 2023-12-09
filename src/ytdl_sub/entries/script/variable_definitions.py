from dataclasses import dataclass
from typing import Optional

# This file contains mixins to a BaseEntry subclass. Ignore pylint's "no kwargs member" suggestion
# pylint: disable=no-member
# pylint: disable=too-many-public-methods


@dataclass(frozen=True)
class Variable:
    variable_name: str


@dataclass(frozen=True)
class InternalVariable(Variable):
    pass


@dataclass(frozen=True)
class Metadata(Variable):
    pass


@dataclass(frozen=True)
class MetadataVariable(Variable):
    metadata_key: str


@dataclass(frozen=True)
class RelativeMetadata(MetadataVariable, Metadata):
    pass


@dataclass(frozen=True)
class SiblingMetadata(MetadataVariable):
    pass


class _Variables:
    @property
    def entry_metadata(self) -> Metadata:
        """
        Returns
        -------
        dict
            The entry's info.json in dict form
        """
        return Metadata("entry_metadata")

    @property
    def playlist_metadata(self) -> RelativeMetadata:
        return RelativeMetadata("playlist_metadata", metadata_key="playlist_metadata")

    @property
    def source_metadata(self) -> RelativeMetadata:
        return RelativeMetadata("source_metadata", metadata_key="source_metadata")

    @property
    def sibling_entry_metadata(self) -> SiblingMetadata:
        return SiblingMetadata("sibling_entry_metadata", metadata_key="sibling_entry_metadata")

    @property
    def uid(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The entry's unique ID
        """
        return MetadataVariable(metadata_key="id", variable_name="uid")

    @property
    def uid_sanitized(self) -> Variable:
        """
        Returns
        -------
        str
            The sanitized uid of the entry, which is safe to use for Unix and Windows file names.
        """
        return Variable("uid_sanitized")

    @property
    def uid_sanitized_plex(self) -> Variable:
        """
        Returns
        -------
        str
            The sanitized uid with additional sanitizing for Plex. Replaces numbers with
            fixed-width numbers so Plex does not recognize them as season or episode numbers.
        """
        return Variable("uid_sanitized_plex")

    @property
    def extractor_key(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The info-extractor key
        """
        return MetadataVariable(metadata_key="extractor_key", variable_name="extractor_key")

    @property
    def extractor(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The ytdl extractor name
        """
        return MetadataVariable(variable_name="extractor", metadata_key="extractor")

    @property
    def epoch(self) -> MetadataVariable:
        """
        Returns
        -------
        int
            The unix epoch of when the metadata was scraped by yt-dlp.
        """
        return MetadataVariable(metadata_key="epoch", variable_name="epoch")

    @property
    def epoch_date(self) -> Variable:
        """
        Returns
        -------
        str
            The epoch's date, in YYYYMMDD format.
        """
        return Variable("epoch_date")

    @property
    def epoch_hour(self) -> Variable:
        """
        Returns
        -------
        str
            The epoch's hour, padded
        """
        return Variable("epoch_hour")

    @property
    def title(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The title of the entry. If a title does not exist, returns its unique ID.
        """
        return MetadataVariable(variable_name="title", metadata_key="title")

    @property
    def title_sanitized(self) -> Variable:
        """
        Returns
        -------
        str
            The sanitized title of the entry, which is safe to use for Unix and Windows file names.
        """
        return Variable("title_sanitized")

    @property
    def title_sanitized_plex(self) -> Variable:
        """
        Returns
        -------
        str
            The sanitized title with additional sanitizing for Plex. Replaces numbers with
            fixed-width numbers so Plex does not recognize them as season or episode numbers.
        """
        return Variable("title_sanitized_plex")

    @property
    def webpage_url(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The url to the webpage.
        """
        return MetadataVariable(metadata_key="webpage_url", variable_name="webpage_url")

    @property
    def info_json_ext(self) -> Variable:
        """
        Returns
        -------
        str
            The "info.json" extension
        """
        return Variable("info_json_ext")

    @property
    def description(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The description if it exists. Otherwise, returns an emtpy string.
        """
        return MetadataVariable(variable_name="description", metadata_key="description")

    @property
    def uploader_id(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The uploader id if it exists, otherwise return the unique ID.
        """
        return MetadataVariable(variable_name="uploader_id", metadata_key="uploader_id")

    @property
    def uploader(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The uploader if it exists, otherwise return the uploader ID.
        """
        return MetadataVariable(variable_name="uploader", metadata_key="uploader")

    @property
    def uploader_url(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The uploader url if it exists, otherwise returns the webpage_url.
        """
        return MetadataVariable("uploader_url", metadata_key="uploader_url")

    @property
    def source_title(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            Name of the source (i.e. channel with multiple playlists) if it exists, otherwise
            returns its playlist_title.
        """
        return MetadataVariable("source_title", metadata_key=self.title.metadata_key)

    @property
    def source_title_sanitized(self) -> Variable:
        """
        Returns
        -------
        str
            The source title, sanitized
        """
        return Variable("source_title_sanitized")

    @property
    def source_uid(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The source unique id if it exists, otherwise returns the playlist unique ID.
        """
        return MetadataVariable("source_uid", metadata_key=self.uid.metadata_key)

    @property
    def source_index(self) -> MetadataVariable:
        """
        Returns
        -------
        int
            Source index if it exists, otherwise returns ``1``.

            It is recommended to not use this unless you know the source will never add new content
            (it is easy for this value to change).
        """
        return MetadataVariable("source_index", metadata_key=self.playlist_index.metadata_key)

    @property
    def source_index_padded(self) -> Variable:
        """
        Returns
        -------
        int
            The source index, padded.
        """
        return Variable("source_index_padded")

    @property
    def source_count(self) -> MetadataVariable:
        """
        Returns
        -------
        int
            The source count if it exists, otherwise returns the playlist count.
        """
        return MetadataVariable("source_count", metadata_key=self.playlist_count.metadata_key)

    @property
    def source_webpage_url(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The source webpage url if it exists, otherwise returns the playlist webpage url.
        """
        return MetadataVariable("source_webpage_url", metadata_key=self.webpage_url.metadata_key)

    @property
    def source_description(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The source description if it exists, otherwise returns the playlist description.
        """
        return MetadataVariable("source_description", metadata_key=self.description.metadata_key)

    @property
    def playlist_uid(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The playlist unique ID if it exists, otherwise return Variable("")
        """
        return MetadataVariable(variable_name="playlist_uid", metadata_key=self.uid.metadata_key)

    @property
    def playlist_title(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            Name of its parent playlist/channel if it exists, otherwise returns its title.
        """
        return MetadataVariable(
            variable_name="playlist_title", metadata_key=self.title.metadata_key
        )

    @property
    def playlist_title_sanitized(self) -> Variable:
        """
        Returns
        -------
        str
            The playlist name, sanitized
        """
        return Variable("playlist_title_sanitized")

    @property
    def playlist_index(self) -> MetadataVariable:
        """
        Returns
        -------
        int
            Playlist index if it exists, otherwise returns ``1``.

            Note that for channels/playlists, any change (i.e. adding or removing a video) will make
            this value change. Use with caution.
        """
        return MetadataVariable(metadata_key="playlist_index", variable_name="playlist_index")

    @property
    def playlist_index_reversed(self) -> Variable:
        """
        Returns
        -------
        int
            Playlist index reversed via ``playlist_count - playlist_index + 1``
        """
        return Variable("playlist_index_reversed")

    @property
    def playlist_index_padded(self) -> Variable:
        """
        Returns
        -------
        str
            playlist_index padded two digits
        """
        return Variable("playlist_index_padded")

    @property
    def playlist_index_reversed_padded(self) -> Variable:
        """
        Returns
        -------
        str
            playlist_index_reversed padded two digits
        """
        return Variable("playlist_index_reversed_padded")

    @property
    def playlist_index_padded6(self) -> Variable:
        """
        Returns
        -------
        str
            playlist_index padded six digits.
        """
        return Variable("playlist_index_padded6")

    @property
    def playlist_index_reversed_padded6(self) -> Variable:
        """
        Returns
        -------
        str
            playlist_index_reversed padded six digits.
        """
        return Variable("playlist_index_reversed_padded6")

    @property
    def playlist_count(self) -> MetadataVariable:
        """
        Returns
        -------
        int
            Playlist count if it exists, otherwise returns ``1``.

            Note that for channels/playlists, any change (i.e. adding or removing a video) will make
            this value change. Use with caution.
        """
        return MetadataVariable(variable_name="playlist_count", metadata_key="playlist_count")

    @property
    def playlist_description(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The playlist description if it exists, otherwise returns the entry's description.
        """
        return MetadataVariable(
            variable_name="playlist_description", metadata_key=self.description.metadata_key
        )

    @property
    def playlist_webpage_url(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The playlist webpage url if it exists. Otherwise, returns the entry webpage url.
        """
        return MetadataVariable(
            variable_name="playlist_webpage_url", metadata_key=self.webpage_url.metadata_key
        )

    @property
    def playlist_max_upload_year(self) -> MetadataVariable:
        """
        Returns
        -------
        int
            Max upload_year for all entries in this entry's playlist if it exists, otherwise returns
            ``upload_year``
        """
        # override in EntryParent
        return MetadataVariable(
            variable_name="playlist_max_upload_year", metadata_key="playlist_max_upload_year"
        )

    @property
    def playlist_max_upload_year_truncated(self) -> Variable:
        """
        Returns
        -------
        int
            The max playlist truncated upload year for all entries in this entry's playlist if it
            exists, otherwise returns ``upload_year_truncated``.
        """
        return Variable("playlist_max_upload_year_truncated")

    @property
    def playlist_uploader_id(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The playlist uploader id if it exists, otherwise returns the entry uploader ID.
        """
        return MetadataVariable("playlist_uploader_id", metadata_key=self.uploader_id.metadata_key)

    @property
    def playlist_uploader(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The playlist uploader if it exists, otherwise return Variable("")
        """
        return MetadataVariable("playlist_uploader", metadata_key=self.uploader.metadata_key)

    @property
    def playlist_uploader_sanitized(self) -> Variable:
        """
        Returns
        -------
        str
            The playlist uploader, sanitized.
        """
        return Variable("playlist_uploader_sanitized")

    @property
    def playlist_uploader_url(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The playlist uploader url if it exists, otherwise returns the playlist webpage_url.
        """
        return MetadataVariable(
            "playlist_uploader_url", metadata_key=self.uploader_url.metadata_key
        )

    @property
    def source_uploader_id(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The source uploader id if it exists, otherwise returns the playlist_uploader_id
        """
        return MetadataVariable("source_uploader_id", metadata_key=self.uploader_id.metadata_key)

    @property
    def source_uploader(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The source uploader if it exists, otherwise return Variable("")
        """
        return MetadataVariable("source_uploader", metadata_key=self.uploader.metadata_key)

    @property
    def source_uploader_url(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The source uploader url if it exists, otherwise returns the source webpage_url.
        """
        return MetadataVariable("source_uploader_url", metadata_key=self.uploader_url.metadata_key)

    @property
    def creator(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The creator name if it exists, otherwise returns the channel.
        """
        return MetadataVariable(variable_name="creator", metadata_key="creator")

    @property
    def creator_sanitized(self) -> Variable:
        """
        Returns
        -------
        str
            The creator name, sanitized
        """
        return Variable("creator_sanitized")

    @property
    def channel(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The channel name if it exists, otherwise returns the uploader.
        """
        return MetadataVariable(variable_name="channel", metadata_key="channel")

    @property
    def channel_sanitized(self) -> Variable:
        """
        Returns
        -------
        str
            The channel name, sanitized.
        """
        return Variable("channel_sanitized")

    @property
    def channel_id(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The channel id if it exists, otherwise returns the entry uploader ID.
        """
        return MetadataVariable(variable_name="channel_id", metadata_key="channel_id")

    @property
    def ext(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The downloaded entry's file extension
        """
        return MetadataVariable(variable_name="ext", metadata_key="ext")

    @property
    def thumbnail_ext(self) -> Variable:
        """
        Returns
        -------
        str
            The download entry's thumbnail extension. Will always return 'jpg'. Until there is a
            need to support other image types, we always convert to jpg.
        """
        return Variable("thumbnail_ext")

    @property
    def comments(self) -> MetadataVariable:
        return MetadataVariable("comments", "comments")

    @property
    def sponsorblock_chapters(self) -> MetadataVariable:
        return MetadataVariable("sponsorblock_chapters", "sponsorblock_chapters")

    @property
    def requested_subtitles(self) -> MetadataVariable:
        return MetadataVariable("requested_subtitles", "requested_subtitles")

    @property
    def ytdl_sub_input_url(self) -> Variable:
        return Variable("ytdl_sub_input_url")

    @property
    def download_index(self) -> Variable:
        """
        Returns
        -------
        int
            The i'th entry downloaded. NOTE that this is fetched dynamically from the download
            archive.
        """
        return Variable(variable_name="download_index")

    @property
    def download_index_padded6(self) -> Variable:
        """
        Returns
        -------
        str
            The download_index padded six digits
        """
        return Variable("download_index_padded6")

    @property
    def upload_date_index(self) -> Variable:
        """
        Returns
        -------
        int
            The i'th entry downloaded with this upload date.
        """
        return Variable(variable_name="upload_date_index")

    @property
    def upload_date_index_padded(self) -> Variable:
        """
        Returns
        -------
        int
            The upload_date_index padded two digits
        """
        return Variable("upload_date_index_padded")

    @property
    def upload_date_index_reversed(self) -> Variable:
        """
        Returns
        -------
        int
            100 - upload_date_index
        """
        return Variable("upload_date_index_reversed")

    @property
    def upload_date_index_reversed_padded(self) -> Variable:
        """
        Returns
        -------
        int
            The upload_date_index padded two digits
        """
        return Variable("upload_date_index_reversed_padded")

    @property
    def upload_date(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The entry's uploaded date, in YYYYMMDD format. If not present, return Variable("")
        """
        return MetadataVariable(variable_name="upload_date", metadata_key="upload_date")

    @property
    def upload_year(self) -> Variable:
        """
        Returns
        -------
        int
            The entry's upload year
        """
        return Variable("upload_year")

    @property
    def upload_year_truncated(self) -> Variable:
        """
        Returns
        -------
        int
            The last two digits of the upload year, i.e. 22 in 2022
        """
        return Variable("upload_year_truncated")

    @property
    def upload_year_truncated_reversed(self) -> Variable:
        """
        Returns
        -------
        int
            The upload year truncated, but reversed using ``100 - {upload_year_truncated}``, i.e.
            2022 returns ``100 - 22`` = ``78``
        """
        return Variable("upload_year_truncated_reversed")

    @property
    def upload_month_reversed(self) -> Variable:
        """
        Returns
        -------
        int
            The upload month, but reversed using ``13 - {upload_month}``, i.e. March returns ``10``
        """
        return Variable("upload_month_reversed")

    @property
    def upload_month_reversed_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The reversed upload month, but padded. i.e. November returns "02"
        """
        return Variable("upload_month_reversed_padded")

    @property
    def upload_month_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The entry's upload month padded to two digits, i.e. March returns "03"
        """
        return Variable("upload_month_padded")

    @property
    def upload_day_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The entry's upload day padded to two digits, i.e. the fifth returns "05"
        """
        return Variable("upload_day_padded")

    @property
    def upload_month(self) -> Variable:
        """
        Returns
        -------
        int
            The upload month as an integer (no padding).
        """
        return Variable("upload_month")

    @property
    def upload_day(self) -> Variable:
        """
        Returns
        -------
        int
            The upload day as an integer (no padding).
        """
        return Variable("upload_day")

    @property
    def upload_day_reversed(self) -> Variable:
        """
        Returns
        -------
        int
            The upload day, but reversed using ``{total_days_in_month} + 1 - {upload_day}``,
            i.e. August 8th would have upload_day_reversed of ``31 + 1 - 8`` = ``24``
        """
        return Variable("upload_day_reversed")

    @property
    def upload_day_reversed_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The reversed upload day, but padded. i.e. August 30th returns "02".
        """
        return Variable("upload_day_reversed_padded")

    @property
    def upload_day_of_year(self) -> Variable:
        """
        Returns
        -------
        int
            The day of the year, i.e. February 1st returns ``32``
        """
        return Variable("upload_day_of_year")

    @property
    def upload_day_of_year_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The upload day of year, but padded i.e. February 1st returns "032"
        """
        return Variable("upload_day_of_year_padded")

    @property
    def upload_day_of_year_reversed(self) -> Variable:
        """
        Returns
        -------
        int
            The upload day, but reversed using ``{total_days_in_year} + 1 - {upload_day}``,
            i.e. February 2nd would have upload_day_of_year_reversed of ``365 + 1 - 32`` = ``334``
        """
        return Variable("upload_day_of_year_reversed")

    @property
    def upload_day_of_year_reversed_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The reversed upload day of year, but padded i.e. December 31st returns "001"
        """
        return Variable("upload_day_of_year_reversed_padded")

    @property
    def upload_date_standardized(self) -> Variable:
        """
        Returns
        -------
        str
            The uploaded date formatted as YYYY-MM-DD
        """
        return Variable("upload_date_standardized")

    @property
    def release_date(self) -> MetadataVariable:
        """
        Returns
        -------
        str
            The entry's release date, in YYYYMMDD format. If not present, return Variable("")
        """
        return MetadataVariable(variable_name="release_date", metadata_key="release_date")

    @property
    def release_year(self) -> Variable:
        """
        Returns
        -------
        int
            The entry's release year
        """
        return Variable("release_year")

    @property
    def release_year_truncated(self) -> Variable:
        """
        Returns
        -------
        int
            The last two digits of the release year, i.e. 22 in 2022
        """
        return Variable("release_year_truncated")

    @property
    def release_year_truncated_reversed(self) -> Variable:
        """
        Returns
        -------
        int
            The release year truncated, but reversed using ``100 - {release_year_truncated}``, i.e.
            2022 returns ``100 - 22`` = ``78``
        """
        return Variable("release_year_truncated_reversed")

    @property
    def release_month_reversed(self) -> Variable:
        """
        Returns
        -------
        int
            The release month, but reversed
            using ``13 - {release_month}``, i.e. March returns ``10``
        """
        return Variable("release_month_reversed")

    @property
    def release_month_reversed_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The reversed release month, but padded. i.e. November returns "02"
        """
        return Variable("release_month_reversed_padded")

    @property
    def release_month_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The entry's release month padded to two digits, i.e. March returns "03"
        """
        return Variable("release_month_padded")

    @property
    def release_day_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The entry's release day padded to two digits, i.e. the fifth returns "05"
        """
        return Variable("release_day_padded")

    @property
    def release_month(self) -> Variable:
        """
        Returns
        -------
        int
            The release month as an integer (no padding).
        """
        return Variable("release_month")

    @property
    def release_day(self) -> Variable:
        """
        Returns
        -------
        int
            The release day as an integer (no padding).
        """
        return Variable("release_day")

    @property
    def release_day_reversed(self) -> Variable:
        """
        Returns
        -------
        int
            The release day, but reversed using ``{total_days_in_month} + 1 - {release_day}``,
            i.e. August 8th would have release_day_reversed of ``31 + 1 - 8`` = ``24``
        """
        return Variable("release_day_reversed")

    @property
    def release_day_reversed_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The reversed release day, but padded. i.e. August 30th returns "02".
        """
        return Variable("release_day_reversed_padded")

    @property
    def release_day_of_year(self) -> Variable:
        """
        Returns
        -------
        int
            The day of the year, i.e. February 1st returns ``32``
        """
        return Variable("release_day_of_year")

    @property
    def release_day_of_year_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The release day of year, but padded i.e. February 1st returns "032"
        """
        return Variable("release_day_of_year_padded")

    @property
    def release_day_of_year_reversed(self) -> Variable:
        """
        Returns
        -------
        int
            The release day, but reversed using ``{total_days_in_year} + 1 - {release_day}``,
            i.e. February 2nd would have release_day_of_year_reversed of ``365 + 1 - 32`` = ``334``
        """
        return Variable("release_day_of_year_reversed")

    @property
    def release_day_of_year_reversed_padded(self) -> Variable:
        """
        Returns
        -------
        str
            The reversed release day of year, but padded i.e. December 31st returns "001"
        """
        return Variable("release_day_of_year_reversed_padded")

    @property
    def release_date_standardized(self) -> Variable:
        """
        Returns
        -------
        str
            The release date formatted as YYYY-MM-DD
        """
        return Variable("release_date_standardized")


# Singleton to use externally
VARIABLES = _Variables()
