from abc import ABC
from typing import Dict
from typing import Set

from ytdl_sub.entries.script.custom_functions import CustomFunctions
from ytdl_sub.entries.script.variable_types import ArrayMetadataVariable
from ytdl_sub.entries.script.variable_types import IntegerMetadataVariable
from ytdl_sub.entries.script.variable_types import IntegerVariable
from ytdl_sub.entries.script.variable_types import MapMetadataVariable
from ytdl_sub.entries.script.variable_types import MapVariable
from ytdl_sub.entries.script.variable_types import MetadataVariable
from ytdl_sub.entries.script.variable_types import StringDateVariable
from ytdl_sub.entries.script.variable_types import StringMetadataVariable
from ytdl_sub.entries.script.variable_types import StringVariable

# This file contains mixins to a BaseEntry subclass. Ignore pylint's "no kwargs member" suggestion
# pylint: disable=no-member
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines


class MetadataVariableDefinitions(ABC):
    @property
    def entry_metadata(self: "VariableDefinitions") -> MapVariable:
        """
        The entry's info.json
        """
        return MapVariable(variable_name="entry_metadata", definition="{ {} }")

    @property
    def playlist_metadata(self: "VariableDefinitions") -> MapMetadataVariable:
        """
        Metadata from the playlist (i.e. the parent metadata, like playlist -> entry)
        """
        return MapMetadataVariable.from_entry(
            metadata_key="playlist_metadata",
            default={},
        )

    @property
    def source_metadata(self: "VariableDefinitions") -> MapMetadataVariable:
        """
        Metadata from the source (i.e. the grandparent metadata, like channel -> playlist -> entry)
        """
        return MapMetadataVariable.from_entry(
            metadata_key="source_metadata",
            default={},
        )

    @property
    def sibling_metadata(self: "VariableDefinitions") -> ArrayMetadataVariable:
        """
        Metadata from any sibling entries that reside in the same playlist as this entry.
        """
        return ArrayMetadataVariable.from_entry(
            metadata_key="sibling_metadata",
            default=[],
        )


class PlaylistVariableDefinitions(ABC):
    @property
    def playlist_uid(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The playlist unique ID if it exists, otherwise return the entry unique ID.
        """
        return StringMetadataVariable.from_playlist(
            metadata_key="playlist_id", variable_name="playlist_uid", default=self.uid
        )

    @property
    def playlist_title(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        Name of its parent playlist/channel if it exists, otherwise returns its title.
        """
        return StringMetadataVariable.from_playlist(
            metadata_key="playlist_title", default=self.title
        )

    @property
    def playlist_index(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        Playlist index if it exists, otherwise returns ``1``.

        Note that for channels/playlists, any change (i.e. adding or removing a video) will make
        this value change. Use with caution.
        """
        return IntegerMetadataVariable.from_entry(metadata_key="playlist_index", default=1)

    @property
    def playlist_index_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        Playlist index reversed via ``playlist_count - playlist_index + 1``
        """
        return IntegerVariable(
            variable_name="playlist_index_reversed",
            definition=f"""{{
                %sub(
                    {self.playlist_count.variable_name},
                    {self.playlist_index.variable_name},
                    -1
                )
            }}""",
        )

    @property
    def playlist_index_padded(self: "VariableDefinitions") -> StringVariable:
        """
        playlist_index padded two digits
        """
        return self.playlist_index.to_padded_int(variable_name="playlist_index_padded", pad=2)

    @property
    def playlist_index_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        playlist_index_reversed padded two digits
        """
        return self.playlist_index_reversed.to_padded_int(
            variable_name="playlist_index_reversed_padded",
            pad=2,
        )

    @property
    def playlist_index_padded6(self: "VariableDefinitions") -> StringVariable:
        """
        playlist_index padded six digits.
        """
        return self.playlist_index.to_padded_int(variable_name="playlist_index_padded6", pad=6)

    @property
    def playlist_index_reversed_padded6(self: "VariableDefinitions") -> StringVariable:
        """
        playlist_index_reversed padded six digits.
        """
        return self.playlist_index_reversed.to_padded_int(
            variable_name="playlist_index_reversed_padded6", pad=6
        )

    @property
    def playlist_count(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        Playlist count if it exists, otherwise returns ``1``.

        Note that for channels/playlists, any change (i.e. adding or removing a video) will make
        this value change. Use with caution.
        """
        return IntegerMetadataVariable.from_entry(metadata_key="playlist_count", default=1)

    @property
    def playlist_description(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The playlist description if it exists, otherwise returns the entry's description.
        """
        return StringMetadataVariable.from_playlist(
            metadata_key=self.description.metadata_key,
            variable_name="playlist_description",
            default=self.description,
        )

    @property
    def playlist_webpage_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The playlist webpage url if it exists. Otherwise, returns the entry webpage url.
        """
        return StringMetadataVariable.from_playlist(
            metadata_key=self.webpage_url.metadata_key,
            variable_name="playlist_webpage_url",
            default=self.webpage_url,
        )

    @property
    def playlist_max_upload_date(self: "VariableDefinitions") -> StringDateVariable:
        """
        Max upload_date for all entries in this entry's playlist if it exists, otherwise returns
        ``upload_date``
        """
        return StringVariable(
            variable_name="playlist_max_upload_date",
            definition=f"""{{
                %array_reduce(
                    %if_passthrough(
                        %extract_field_from_siblings('{self.upload_date.variable_name}'),
                        [{self.upload_date.variable_name}]
                    ),
                    %max
                )
            }}""",
        ).as_date_variable()

    @property
    def playlist_max_upload_year(self: "VariableDefinitions") -> IntegerVariable:
        """
        Max upload_year for all entries in this entry's playlist if it exists, otherwise returns
        ``upload_year``
        """
        return self.playlist_max_upload_date.get_integer_date_metadata(
            date_metadata_key="year",
            variable_name="playlist_max_upload_year",
        )

    @property
    def playlist_max_upload_year_truncated(self: "VariableDefinitions") -> IntegerVariable:
        """
        The max playlist truncated upload year for all entries in this entry's playlist if it
        exists, otherwise returns ``upload_year_truncated``.
        """
        return self.playlist_max_upload_date.get_integer_date_metadata(
            date_metadata_key="year_truncated", variable_name="playlist_max_upload_year_truncated"
        )

    @property
    def playlist_uploader_id(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The playlist uploader id if it exists, otherwise returns the entry uploader ID.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="playlist_uploader_id",
            default=self.uploader_id,
        )

    @property
    def playlist_uploader(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The playlist uploader if it exists, otherwise return the entry uploader.
        """
        return StringMetadataVariable.from_playlist(
            metadata_key=self.uploader.metadata_key,
            variable_name="playlist_uploader",
            default=self.uploader,
        )

    @property
    def playlist_uploader_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The playlist uploader url if it exists, otherwise returns the playlist webpage_url.
        """
        return StringMetadataVariable.from_playlist(
            metadata_key=self.uploader_url.metadata_key,
            variable_name="playlist_uploader_url",
            default=self.webpage_url,
        )


class SourceVariableDefinitions(ABC):
    @property
    def source_title(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        Name of the source (i.e. channel with multiple playlists) if it exists, otherwise
        returns its playlist_title.
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.title.metadata_key,
            variable_name="source_title",
            default=self.playlist_title,
        )

    @property
    def source_uid(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The source unique id if it exists, otherwise returns the playlist unique ID.
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.uid.metadata_key,
            variable_name="source_uid",
            default=self.playlist_uid,
        )

    @property
    def source_index(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        Source index if it exists, otherwise returns ``1``.

        It is recommended to not use this unless you know the source will never add new content
        (it is easy for this value to change).
        """
        return IntegerMetadataVariable.from_playlist(
            metadata_key=self.playlist_index.metadata_key,
            variable_name="source_index",
            default=1,
        )

    @property
    def source_index_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The source index, padded two digits.
        """
        return self.source_index.to_padded_int(variable_name="source_index_padded", pad=2)

    @property
    def source_count(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        The source count if it exists, otherwise returns ``1``.
        """
        return IntegerMetadataVariable.from_playlist(
            metadata_key=self.playlist_count.metadata_key,
            variable_name="source_count",
            default=1,
        )

    @property
    def source_webpage_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The source webpage url if it exists, otherwise returns the playlist webpage url.
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.webpage_url.metadata_key,
            variable_name="source_webpage_url",
            default=self.playlist_webpage_url,
        )

    @property
    def source_description(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The source description if it exists, otherwise returns the playlist description.
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.description.metadata_key,
            variable_name="source_description",
            default=self.playlist_description,
        )

    @property
    def source_uploader_id(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The source uploader id if it exists, otherwise returns the playlist_uploader_id
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.uploader_id.metadata_key,
            variable_name="source_uploader_id",
            default=self.playlist_uploader_id,
        )

    @property
    def source_uploader(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The source uploader if it exists, otherwise return the playlist_uploader
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.uploader.metadata_key,
            variable_name="source_uploader",
            default=self.playlist_uploader,
        )

    @property
    def source_uploader_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The source uploader url if it exists, otherwise returns the source webpage_url.
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.uploader_url.metadata_key,
            variable_name="source_uploader_url",
            default=self.source_webpage_url,
        )


class UploadDateVariableDefinitions(ABC):
    @property
    def upload_date(self: "VariableDefinitions") -> StringDateVariable:
        """
        The entry’s uploaded date, in YYYYMMDD format. If not present, return today’s date.
        """
        return StringMetadataVariable.from_entry(metadata_key="upload_date").as_date_variable()

    @property
    def upload_year(self: "VariableDefinitions") -> IntegerVariable:
        """
        The entry's upload year
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="year", variable_name="upload_year"
        )

    @property
    def upload_year_truncated(self: "VariableDefinitions") -> IntegerVariable:
        """
        The last two digits of the upload year, i.e. 22 in 2022
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="year_truncated", variable_name="upload_year_truncated"
        )

    @property
    def upload_year_truncated_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload year truncated, but reversed using ``100 - {upload_year_truncated}``, i.e.
        2022 returns ``100 - 22`` = ``78``
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="year_truncated_reversed",
            variable_name="upload_year_truncated_reversed",
        )

    @property
    def upload_month_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload month, but reversed using ``13 - {upload_month}``, i.e. March returns ``10``
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="month_reversed", variable_name="upload_month_reversed"
        )

    @property
    def upload_month_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The reversed upload month, but padded. i.e. November returns "02"
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="month_reversed_padded", variable_name="upload_month_reversed_padded"
        )

    @property
    def upload_month_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The entry's upload month padded to two digits, i.e. March returns "03"
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="month_padded", variable_name="upload_month_padded"
        )

    @property
    def upload_day_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The entry's upload day padded to two digits, i.e. the fifth returns "05"
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="day_padded", variable_name="upload_day_padded"
        )

    @property
    def upload_month(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload month as an integer (no padding).
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="month", variable_name="upload_month"
        )

    @property
    def upload_day(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload day as an integer (no padding).
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="day", variable_name="upload_day"
        )

    @property
    def upload_day_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload day, but reversed using ``{total_days_in_month} + 1 - {upload_day}``,
        i.e. August 8th would have upload_day_reversed of ``31 + 1 - 8`` = ``24``
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="day_reversed", variable_name="upload_day_reversed"
        )

    @property
    def upload_day_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The reversed upload day, but padded. i.e. August 30th returns "02".
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="day_reversed_padded", variable_name="upload_day_reversed_padded"
        )

    @property
    def upload_day_of_year(self: "VariableDefinitions") -> IntegerVariable:
        """
        The day of the year, i.e. February 1st returns ``32``
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="day_of_year", variable_name="upload_day_of_year"
        )

    @property
    def upload_day_of_year_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The upload day of year, but padded i.e. February 1st returns "032"
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="day_of_year_padded", variable_name="upload_day_of_year_padded"
        )

    @property
    def upload_day_of_year_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload day, but reversed using ``{total_days_in_year} + 1 - {upload_day}``,
        i.e. February 2nd would have upload_day_of_year_reversed of ``365 + 1 - 32`` = ``334``
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="day_of_year_reversed", variable_name="upload_day_of_year_reversed"
        )

    @property
    def upload_day_of_year_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The reversed upload day of year, but padded i.e. December 31st returns "001"
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="day_of_year_reversed_padded",
            variable_name="upload_day_of_year_reversed_padded",
        )

    @property
    def upload_date_standardized(self: "VariableDefinitions") -> StringVariable:
        """
        The uploaded date formatted as YYYY-MM-DD
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="date_standardized", variable_name="upload_date_standardized"
        )


class ReleaseDateVariableDefinitions(ABC):
    @property
    def release_date(self: "VariableDefinitions") -> StringDateVariable:
        """
        The entry’s release date, in YYYYMMDD format. If not present, return the upload date.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="release_date", default=self.upload_date
        ).as_date_variable()

    @property
    def release_year(self: "VariableDefinitions") -> IntegerVariable:
        """
        The entry's upload year
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="year", variable_name="release_year"
        )

    @property
    def release_year_truncated(self: "VariableDefinitions") -> IntegerVariable:
        """
        The last two digits of the upload year, i.e. 22 in 2022
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="year_truncated", variable_name="release_year_truncated"
        )

    @property
    def release_year_truncated_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload year truncated, but reversed using ``100 - {release_year_truncated}``, i.e.
        2022 returns ``100 - 22`` = ``78``
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="year_truncated_reversed",
            variable_name="release_year_truncated_reversed",
        )

    @property
    def release_month_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload month, but reversed using ``13 - {release_month}``, i.e. March returns ``10``
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="month_reversed", variable_name="release_month_reversed"
        )

    @property
    def release_month_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The reversed upload month, but padded. i.e. November returns "02"
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="month_reversed_padded", variable_name="release_month_reversed_padded"
        )

    @property
    def release_month_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The entry's upload month padded to two digits, i.e. March returns "03"
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="month_padded", variable_name="release_month_padded"
        )

    @property
    def release_day_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The entry's upload day padded to two digits, i.e. the fifth returns "05"
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="day_padded", variable_name="release_day_padded"
        )

    @property
    def release_month(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload month as an integer (no padding).
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="month", variable_name="release_month"
        )

    @property
    def release_day(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload day as an integer (no padding).
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="day", variable_name="release_day"
        )

    @property
    def release_day_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload day, but reversed using ``{total_days_in_month} + 1 - {release_day}``,
        i.e. August 8th would have release_day_reversed of ``31 + 1 - 8`` = ``24``
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="day_reversed", variable_name="release_day_reversed"
        )

    @property
    def release_day_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The reversed upload day, but padded. i.e. August 30th returns "02".
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="day_reversed_padded", variable_name="release_day_reversed_padded"
        )

    @property
    def release_day_of_year(self: "VariableDefinitions") -> IntegerVariable:
        """
        The day of the year, i.e. February 1st returns ``32``
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="day_of_year", variable_name="release_day_of_year"
        )

    @property
    def release_day_of_year_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The upload day of year, but padded i.e. February 1st returns "032"
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="day_of_year_padded", variable_name="release_day_of_year_padded"
        )

    @property
    def release_day_of_year_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        The upload day, but reversed using ``{total_days_in_year} + 1 - {release_day}``,
        i.e. February 2nd would have release_day_of_year_reversed of ``365 + 1 - 32`` = ``334``
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="day_of_year_reversed", variable_name="release_day_of_year_reversed"
        )

    @property
    def release_day_of_year_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The reversed upload day of year, but padded i.e. December 31st returns "001"
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="day_of_year_reversed_padded",
            variable_name="release_day_of_year_reversed_padded",
        )

    @property
    def release_date_standardized(self: "VariableDefinitions") -> StringVariable:
        """
        The uploaded date formatted as YYYY-MM-DD
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="date_standardized", variable_name="release_date_standardized"
        )


class YtdlSubVariableDefinitions(ABC):
    @property
    def ytdl_sub_input_url(self: "VariableDefinitions") -> StringVariable:
        """
        The input URL used in ytdl-sub to create this entry.
        """
        return StringVariable(variable_name="ytdl_sub_input_url", definition="{ %string('') }")

    @property
    def download_index(self: "VariableDefinitions") -> IntegerVariable:
        """
        The i'th entry downloaded. NOTE that this is fetched dynamically from the download
        archive.
        """
        return IntegerVariable(variable_name="download_index", definition="{ %int(1) }")

    @property
    def download_index_padded6(self: "VariableDefinitions") -> StringVariable:
        """
        The download_index padded six digits
        """
        return self.download_index.to_padded_int(variable_name="download_index_padded6", pad=6)

    @property
    def upload_date_index(self: "VariableDefinitions") -> IntegerVariable:
        """
        The i'th entry downloaded with this upload date.
        """
        return IntegerVariable(variable_name="upload_date_index", definition="{ %int(1) }")

    @property
    def upload_date_index_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The upload_date_index padded two digits
        """
        return self.upload_date_index.to_padded_int(variable_name="upload_date_index_padded", pad=2)

    @property
    def upload_date_index_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        100 - upload_date_index
        """
        return IntegerVariable(
            variable_name="upload_date_index_reversed",
            definition=f"{{%sub(100, {self.upload_date_index.variable_name})}}",
        )

    @property
    def upload_date_index_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        The upload_date_index padded two digits
        """
        return self.upload_date_index_reversed.to_padded_int(
            variable_name="upload_date_index_reversed_padded", pad=2
        )


class EntryVariableDefinitions(ABC):
    @property
    def uid(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The entry's unique ID
        """
        return StringMetadataVariable.from_entry(metadata_key="id", variable_name="uid")

    @property
    def duration(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        The duration of the entry in seconds if it exists. Defaults to zero otherwise.
        """
        return IntegerMetadataVariable.from_entry(metadata_key="duration", default=0)

    @property
    def uid_sanitized_plex(self: "VariableDefinitions") -> StringVariable:
        """
        The sanitized uid with additional sanitizing for Plex. Replaces numbers with
        fixed-width numbers so Plex does not recognize them as season or episode numbers.
        """
        return self.uid.to_sanitized_plex(variable_name="uid_sanitized_plex")

    @property
    def ie_key(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The ie_key, used in legacy yt-dlp things as the 'info-extractor key'.
        If it does not exist, return ``extractor_key``
        """
        return StringMetadataVariable.from_entry(metadata_key="ie_key", default=self.extractor_key)

    @property
    def extractor_key(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The yt-dlp extractor key
        """
        return StringMetadataVariable.from_entry(metadata_key="extractor_key")

    @property
    def extractor(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The yt-dlp extractor name
        """
        return StringMetadataVariable.from_entry(metadata_key="extractor")

    @property
    def epoch(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        The unix epoch of when the metadata was scraped by yt-dlp.
        """
        return IntegerMetadataVariable.from_entry(metadata_key="epoch")

    @property
    def epoch_date(self: "VariableDefinitions") -> StringVariable:
        """
        The epoch's date, in YYYYMMDD format.
        """
        return StringVariable(
            variable_name="epoch_date",
            definition=f"{{%datetime_strftime({self.epoch.variable_name}, '%Y%m%d')}}",
        )

    @property
    def epoch_hour(self: "VariableDefinitions") -> StringVariable:
        """
        The epoch's hour
        """
        return StringVariable(
            variable_name="epoch_hour",
            definition=f"{{%datetime_strftime({self.epoch.variable_name}, '%H')}}",
        )

    @property
    def title(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The title of the entry. If a title does not exist, returns its unique ID.
        """
        return StringMetadataVariable.from_entry(metadata_key="title", default=self.uid)

    @property
    def title_sanitized_plex(self: "VariableDefinitions") -> StringVariable:
        """
        The sanitized title with additional sanitizing for Plex. It replaces numbers with
        fixed-width numbers so Plex does not recognize them as season or episode numbers.
        """
        return self.title.to_sanitized_plex(variable_name="title_sanitized_plex")

    @property
    def webpage_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The url to the webpage.
        """
        return StringMetadataVariable.from_entry(metadata_key="webpage_url")

    @property
    def info_json_ext(self: "VariableDefinitions") -> StringVariable:
        """
        The "info.json" extension
        """
        return StringVariable(
            variable_name="info_json_ext",
            definition="info.json",
        )

    @property
    def description(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The description if it exists. Otherwise, returns an emtpy string.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="description",
            default="",
        )

    @property
    def uploader_id(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The uploader id if it exists, otherwise return the unique ID.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="uploader_id",
            default=self.uid,
        )

    @property
    def uploader(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The uploader if it exists, otherwise return the uploader ID.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="uploader",
            default=self.uploader_id,
        )

    @property
    def uploader_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The uploader url if it exists, otherwise returns the webpage_url.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="uploader_url",
            default=self.webpage_url,
        )

    @property
    def creator(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The creator name if it exists, otherwise returns the channel.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="creator",
            default=self.channel,
        )

    @property
    def channel(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The channel name if it exists, otherwise returns the uploader.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="channel",
            default=self.uploader,
        )

    @property
    def channel_id(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The channel id if it exists, otherwise returns the entry uploader ID.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="channel_id",
            default=self.uploader_id,
        )

    @property
    def ext(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        The downloaded entry's file extension
        """
        return StringMetadataVariable.from_entry(metadata_key="ext")

    @property
    def thumbnail_ext(self: "VariableDefinitions") -> StringVariable:
        """
        The download entry's thumbnail extension. Will always return 'jpg'. Until there is a
        need to support other image types, we always convert to jpg.
        """
        return StringVariable(
            variable_name="thumbnail_ext",
            definition="jpg",
        )

    @property
    def comments(self: "VariableDefinitions") -> ArrayMetadataVariable:
        """
        Comments if they are requested
        """
        return ArrayMetadataVariable(
            metadata_key="comments", variable_name="comments", definition="{ [] }"
        )

    @property
    def chapters(self: "VariableDefinitions") -> ArrayMetadataVariable:
        """
        Chapters if they exist
        """
        return ArrayMetadataVariable(
            metadata_key="chapters", variable_name="chapters", definition="{ [] }"
        )

    @property
    def sponsorblock_chapters(self: "VariableDefinitions") -> ArrayMetadataVariable:
        """
        Sponsorblock Chapters if they are requested and exist
        """
        return ArrayMetadataVariable(
            metadata_key="sponsorblock_chapters",
            variable_name="sponsorblock_chapters",
            definition="{ [] }",
        )

    @property
    def requested_subtitles(self: "VariableDefinitions") -> MapMetadataVariable:
        """
        Subtitles if they are requested and exist
        """
        return MapMetadataVariable(
            metadata_key="requested_subtitles",
            variable_name="requested_subtitles",
            definition="{ {} }",
        )


class VariableDefinitions(
    EntryVariableDefinitions,
    MetadataVariableDefinitions,
    PlaylistVariableDefinitions,
    SourceVariableDefinitions,
    UploadDateVariableDefinitions,
    ReleaseDateVariableDefinitions,
    YtdlSubVariableDefinitions,
):
    @classmethod
    def scripts(cls) -> Dict[str, str]:
        """
        Returns all variables and their scripts in dict form
        """
        return {
            property_name: getattr(VARIABLES, property_name).definition
            for property_name in [
                prop for prop in dir(cls) if isinstance(getattr(cls, prop), property)
            ]
        }

    @classmethod
    def injected_variables(cls) -> Set[MetadataVariable]:
        """
        Returns variables that get injected in the download-stage
        """
        return {
            VARIABLES.download_index,
            VARIABLES.comments,
            VARIABLES.requested_subtitles,
            VARIABLES.chapters,
            VARIABLES.sponsorblock_chapters,
            VARIABLES.ytdl_sub_input_url,
        }

    @classmethod
    def required_entry_variables(cls) -> Set[MetadataVariable]:
        """
        Returns variables that the entry requires to exist
        """
        return {
            VARIABLES.uid,
            VARIABLES.extractor_key,
            VARIABLES.epoch,
            VARIABLES.webpage_url,
            VARIABLES.ext,
        }

    @classmethod
    def default_entry_variables(cls) -> Set[MetadataVariable]:
        """
        Returns variables that reside on the entry that may or may not exist,
        but have defaults
        """
        return {
            VARIABLES.title,
            VARIABLES.extractor,
            VARIABLES.description,
            VARIABLES.ie_key,
            VARIABLES.uploader_id,
            VARIABLES.uploader,
            VARIABLES.uploader_url,
            VARIABLES.upload_date,
            VARIABLES.release_date,
            VARIABLES.channel,
            VARIABLES.creator,
            VARIABLES.channel_id,
            VARIABLES.duration,
            VARIABLES.playlist_index,
            VARIABLES.playlist_count,
            VARIABLES.playlist_uid,
            VARIABLES.playlist_title,
            VARIABLES.playlist_uploader_id,
        }

    @classmethod
    def unresolvable_static_variables(cls) -> Set[str]:
        """
        Returns variables that are not static (i.e. depend on runtime)
        """
        return {
            VARIABLES.entry_metadata.variable_name,
        } | cls.injected_variables()


# Singletons to use externally
VARIABLES: VariableDefinitions = VariableDefinitions()
VARIABLE_SCRIPTS: Dict[str, str] = VariableDefinitions.scripts()
UNRESOLVED_VARIABLES: Set[str] = VariableDefinitions.unresolvable_static_variables()

CustomFunctions.register()
