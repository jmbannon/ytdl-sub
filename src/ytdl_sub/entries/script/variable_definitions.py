from abc import ABC
from functools import cache
from functools import cached_property
from typing import Dict
from typing import Set

from ytdl_sub.entries.script.custom_functions import CustomFunctions
from ytdl_sub.entries.script.variable_types import ArrayMetadataVariable
from ytdl_sub.entries.script.variable_types import IntegerMetadataVariable
from ytdl_sub.entries.script.variable_types import IntegerVariable
from ytdl_sub.entries.script.variable_types import MapMetadataVariable
from ytdl_sub.entries.script.variable_types import MapVariable
from ytdl_sub.entries.script.variable_types import MetadataVariable
from ytdl_sub.entries.script.variable_types import StringDateMetadataVariable
from ytdl_sub.entries.script.variable_types import StringDateVariable
from ytdl_sub.entries.script.variable_types import StringMetadataVariable
from ytdl_sub.entries.script.variable_types import StringVariable
from ytdl_sub.entries.script.variable_types import Variable

# This file contains mixins to a BaseEntry subclass. Ignore pylint's "no kwargs member" suggestion
# pylint: disable=no-member
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-lines
# pylint: disable=method-cache-max-size-none


class MetadataVariableDefinitions(ABC):
    @cached_property
    def entry_metadata(self: "VariableDefinitions") -> MapVariable:
        """
        :description:
          The entry's info.json
        """
        return MapVariable(variable_name="entry_metadata", definition="{ {} }")

    @cached_property
    def playlist_metadata(self: "VariableDefinitions") -> MapMetadataVariable:
        """
        :description:
          Metadata from the playlist (i.e. the parent metadata, like playlist -> entry)
        """
        return MapMetadataVariable.from_entry(
            metadata_key="playlist_metadata",
            default={},
        )

    @cached_property
    def source_metadata(self: "VariableDefinitions") -> MapMetadataVariable:
        """
        :description:
          Metadata from the source
          (i.e. the grandparent metadata, like channel -> playlist -> entry)
        """
        return MapMetadataVariable.from_entry(
            metadata_key="source_metadata",
            default={},
        )

    @cached_property
    def sibling_metadata(self: "VariableDefinitions") -> ArrayMetadataVariable:
        """
        :description:
          Metadata from any sibling entries that reside in the same playlist as this entry.
        """
        return ArrayMetadataVariable.from_entry(
            metadata_key="sibling_metadata",
            default=[],
        )


class PlaylistVariableDefinitions(ABC):
    @cached_property
    def playlist_uid(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The playlist unique ID if it exists, otherwise return the entry unique ID.
        """
        return StringMetadataVariable.from_playlist(
            metadata_key="playlist_id", variable_name="playlist_uid", default=self.uid
        )

    @cached_property
    def playlist_title(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          Name of its parent playlist/channel if it exists, otherwise returns its title.
        """
        return StringMetadataVariable.from_entry(metadata_key="playlist_title", default=self.title)

    @cached_property
    def playlist_index(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        :description:
          Playlist index if it exists, otherwise returns ``1``.

          Note that for channels/playlists, any change (i.e. adding or removing a video) will make
          this value change. Use with caution.
        """
        return IntegerMetadataVariable.from_entry(metadata_key="playlist_index", default=1)

    @cached_property
    def playlist_index_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
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

    @cached_property
    def playlist_index_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          playlist_index padded two digits
        """
        return self.playlist_index.to_padded_int(variable_name="playlist_index_padded", pad=2)

    @cached_property
    def playlist_index_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          playlist_index_reversed padded two digits
        """
        return self.playlist_index_reversed.to_padded_int(
            variable_name="playlist_index_reversed_padded",
            pad=2,
        )

    @cached_property
    def playlist_index_padded6(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          playlist_index padded six digits.
        """
        return self.playlist_index.to_padded_int(variable_name="playlist_index_padded6", pad=6)

    @cached_property
    def playlist_index_reversed_padded6(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          playlist_index_reversed padded six digits.
        """
        return self.playlist_index_reversed.to_padded_int(
            variable_name="playlist_index_reversed_padded6", pad=6
        )

    @cached_property
    def playlist_count(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        :description:
          Playlist count if it exists, otherwise returns ``1``.

          Note that for channels/playlists, any change (i.e. adding or removing a video) will make
          this value change. Use with caution.
        """
        return IntegerMetadataVariable.from_entry(metadata_key="playlist_count", default=1)

    @cached_property
    def playlist_description(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The playlist description if it exists, otherwise returns the entry's description.
        """
        return StringMetadataVariable.from_playlist(
            metadata_key=self.description.metadata_key,
            variable_name="playlist_description",
            default=self.description,
        )

    @cached_property
    def playlist_webpage_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The playlist webpage url if it exists. Otherwise, returns the entry webpage url.
        """
        return StringMetadataVariable.from_playlist(
            metadata_key=self.webpage_url.metadata_key,
            variable_name="playlist_webpage_url",
            default=self.webpage_url,
        )

    @cached_property
    def playlist_max_upload_date(self: "VariableDefinitions") -> StringDateVariable:
        """
        :description:
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

    @cached_property
    def playlist_max_upload_year(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          Max upload_year for all entries in this entry's playlist if it exists, otherwise returns
          ``upload_year``
        """
        return self.playlist_max_upload_date.get_integer_date_metadata(
            date_metadata_key="year",
            variable_name="playlist_max_upload_year",
        )

    @cached_property
    def playlist_max_upload_year_truncated(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The max playlist truncated upload year for all entries in this entry's playlist if it
          exists, otherwise returns ``upload_year_truncated``.
        """
        return self.playlist_max_upload_date.get_integer_date_metadata(
            date_metadata_key="year_truncated", variable_name="playlist_max_upload_year_truncated"
        )

    @cached_property
    def playlist_uploader_id(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The playlist uploader id if it exists, otherwise returns the entry uploader ID.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="playlist_uploader_id",
            default=self.uploader_id,
        )

    @cached_property
    def playlist_uploader(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The playlist uploader if it exists, otherwise return the entry uploader.
        """
        return StringMetadataVariable.from_playlist(
            metadata_key=self.uploader.metadata_key,
            variable_name="playlist_uploader",
            default=self.uploader,
        )

    @cached_property
    def playlist_uploader_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The playlist uploader url if it exists, otherwise returns the playlist webpage_url.
        """
        return StringMetadataVariable.from_playlist(
            metadata_key=self.uploader_url.metadata_key,
            variable_name="playlist_uploader_url",
            default=self.webpage_url,
        )


class SourceVariableDefinitions(ABC):
    @cached_property
    def source_title(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          Name of the source (i.e. channel with multiple playlists) if it exists, otherwise
          returns its playlist_title.
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.title.metadata_key,
            variable_name="source_title",
            default=self.playlist_title,
        )

    @cached_property
    def source_uid(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The source unique id if it exists, otherwise returns the playlist unique ID.
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.uid.metadata_key,
            variable_name="source_uid",
            default=self.playlist_uid,
        )

    @cached_property
    def source_index(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        :description:
          Source index if it exists, otherwise returns ``1``.

          It is recommended to not use this unless you know the source will never add new content
          (it is easy for this value to change).
        """
        return IntegerMetadataVariable.from_playlist(
            metadata_key=self.playlist_index.metadata_key,
            variable_name="source_index",
            default=1,
        )

    @cached_property
    def source_index_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The source index, padded two digits.
        """
        return self.source_index.to_padded_int(variable_name="source_index_padded", pad=2)

    @cached_property
    def source_count(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        :description:
          The source count if it exists, otherwise returns ``1``.
        """
        return IntegerMetadataVariable.from_playlist(
            metadata_key=self.playlist_count.metadata_key,
            variable_name="source_count",
            default=1,
        )

    @cached_property
    def source_webpage_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The source webpage url if it exists, otherwise returns the playlist webpage url.
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.webpage_url.metadata_key,
            variable_name="source_webpage_url",
            default=self.playlist_webpage_url,
        )

    @cached_property
    def source_description(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The source description if it exists, otherwise returns the playlist description.
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.description.metadata_key,
            variable_name="source_description",
            default=self.playlist_description,
        )

    @cached_property
    def source_uploader_id(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The source uploader id if it exists, otherwise returns the playlist_uploader_id
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.uploader_id.metadata_key,
            variable_name="source_uploader_id",
            default=self.playlist_uploader_id,
        )

    @cached_property
    def source_uploader(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The source uploader if it exists, otherwise return the playlist_uploader
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.uploader.metadata_key,
            variable_name="source_uploader",
            default=self.playlist_uploader,
        )

    @cached_property
    def source_uploader_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The source uploader url if it exists, otherwise returns the source webpage_url.
        """
        return StringMetadataVariable.from_source(
            metadata_key=self.uploader_url.metadata_key,
            variable_name="source_uploader_url",
            default=self.source_webpage_url,
        )


class UploadDateVariableDefinitions(ABC):
    @cached_property
    def upload_date(self: "VariableDefinitions") -> StringDateMetadataVariable:
        """
        :description:
          The entry’s uploaded date, in YYYYMMDD format. If not present, return today’s date.
        """
        return StringDateMetadataVariable.from_entry(
            metadata_key="upload_date", default=self.epoch_date
        ).as_date_variable()

    @cached_property
    def upload_year(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The entry's upload year
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="year", variable_name="upload_year"
        )

    @cached_property
    def upload_year_truncated(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The last two digits of the upload year, i.e. 22 in 2022
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="year_truncated", variable_name="upload_year_truncated"
        )

    @cached_property
    def upload_year_truncated_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload year truncated, but reversed using ``100 - {upload_year_truncated}``, i.e.
          2022 returns ``100 - 22`` = ``78``
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="year_truncated_reversed",
            variable_name="upload_year_truncated_reversed",
        )

    @cached_property
    def upload_month_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload month, but reversed using ``13 - {upload_month}``, i.e. March returns ``10``
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="month_reversed", variable_name="upload_month_reversed"
        )

    @cached_property
    def upload_month_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The reversed upload month, but padded. i.e. November returns "02"
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="month_reversed_padded", variable_name="upload_month_reversed_padded"
        )

    @cached_property
    def upload_month_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The entry's upload month padded to two digits, i.e. March returns "03"
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="month_padded", variable_name="upload_month_padded"
        )

    @cached_property
    def upload_day_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The entry's upload day padded to two digits, i.e. the fifth returns "05"
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="day_padded", variable_name="upload_day_padded"
        )

    @cached_property
    def upload_month(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload month as an integer (no padding).
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="month", variable_name="upload_month"
        )

    @cached_property
    def upload_day(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload day as an integer (no padding).
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="day", variable_name="upload_day"
        )

    @cached_property
    def upload_day_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload day, but reversed using ``{total_days_in_month} + 1 - {upload_day}``,
          i.e. August 8th would have upload_day_reversed of ``31 + 1 - 8`` = ``24``
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="day_reversed", variable_name="upload_day_reversed"
        )

    @cached_property
    def upload_day_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The reversed upload day, but padded. i.e. August 30th returns "02".
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="day_reversed_padded", variable_name="upload_day_reversed_padded"
        )

    @cached_property
    def upload_day_of_year(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The day of the year, i.e. February 1st returns ``32``
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="day_of_year", variable_name="upload_day_of_year"
        )

    @cached_property
    def upload_day_of_year_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The upload day of year, but padded i.e. February 1st returns "032"
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="day_of_year_padded", variable_name="upload_day_of_year_padded"
        )

    @cached_property
    def upload_day_of_year_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload day, but reversed using ``{total_days_in_year} + 1 - {upload_day}``,
          i.e. February 2nd would have upload_day_of_year_reversed of ``365 + 1 - 32`` = ``334``
        """
        return self.upload_date.get_integer_date_metadata(
            date_metadata_key="day_of_year_reversed", variable_name="upload_day_of_year_reversed"
        )

    @cached_property
    def upload_day_of_year_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The reversed upload day of year, but padded i.e. December 31st returns "001"
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="day_of_year_reversed_padded",
            variable_name="upload_day_of_year_reversed_padded",
        )

    @cached_property
    def upload_date_standardized(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The uploaded date formatted as YYYY-MM-DD
        """
        return self.upload_date.get_string_date_metadata(
            date_metadata_key="date_standardized", variable_name="upload_date_standardized"
        )


class ReleaseDateVariableDefinitions(ABC):
    @cached_property
    def release_date(self: "VariableDefinitions") -> StringDateMetadataVariable:
        """
        :description:
          The entry’s release date, in YYYYMMDD format. If not present, return the upload date.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="release_date", default=self.upload_date
        ).as_date_variable()

    @cached_property
    def release_year(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The entry's upload year
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="year", variable_name="release_year"
        )

    @cached_property
    def release_year_truncated(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The last two digits of the upload year, i.e. 22 in 2022
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="year_truncated", variable_name="release_year_truncated"
        )

    @cached_property
    def release_year_truncated_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload year truncated, but reversed using ``100 - {release_year_truncated}``, i.e.
          2022 returns ``100 - 22`` = ``78``
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="year_truncated_reversed",
            variable_name="release_year_truncated_reversed",
        )

    @cached_property
    def release_month_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload month, but reversed using ``13 - {release_month}``, i.e. March returns ``10``
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="month_reversed", variable_name="release_month_reversed"
        )

    @cached_property
    def release_month_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The reversed upload month, but padded. i.e. November returns "02"
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="month_reversed_padded", variable_name="release_month_reversed_padded"
        )

    @cached_property
    def release_month_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The entry's upload month padded to two digits, i.e. March returns "03"
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="month_padded", variable_name="release_month_padded"
        )

    @cached_property
    def release_day_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The entry's upload day padded to two digits, i.e. the fifth returns "05"
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="day_padded", variable_name="release_day_padded"
        )

    @cached_property
    def release_month(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload month as an integer (no padding).
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="month", variable_name="release_month"
        )

    @cached_property
    def release_day(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload day as an integer (no padding).
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="day", variable_name="release_day"
        )

    @cached_property
    def release_day_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload day, but reversed using ``{total_days_in_month} + 1 - {release_day}``,
          i.e. August 8th would have release_day_reversed of ``31 + 1 - 8`` = ``24``
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="day_reversed", variable_name="release_day_reversed"
        )

    @cached_property
    def release_day_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The reversed upload day, but padded. i.e. August 30th returns "02".
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="day_reversed_padded", variable_name="release_day_reversed_padded"
        )

    @cached_property
    def release_day_of_year(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The day of the year, i.e. February 1st returns ``32``
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="day_of_year", variable_name="release_day_of_year"
        )

    @cached_property
    def release_day_of_year_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The upload day of year, but padded i.e. February 1st returns "032"
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="day_of_year_padded", variable_name="release_day_of_year_padded"
        )

    @cached_property
    def release_day_of_year_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The upload day, but reversed using ``{total_days_in_year} + 1 - {release_day}``,
          i.e. February 2nd would have release_day_of_year_reversed of ``365 + 1 - 32`` = ``334``
        """
        return self.release_date.get_integer_date_metadata(
            date_metadata_key="day_of_year_reversed", variable_name="release_day_of_year_reversed"
        )

    @cached_property
    def release_day_of_year_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The reversed upload day of year, but padded i.e. December 31st returns "001"
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="day_of_year_reversed_padded",
            variable_name="release_day_of_year_reversed_padded",
        )

    @cached_property
    def release_date_standardized(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The uploaded date formatted as YYYY-MM-DD
        """
        return self.release_date.get_string_date_metadata(
            date_metadata_key="date_standardized", variable_name="release_date_standardized"
        )


class YtdlSubVariableDefinitions(ABC):
    @cached_property
    def ytdl_sub_input_url(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The input URL used in ytdl-sub to create this entry.
        """
        return StringVariable(variable_name="ytdl_sub_input_url", definition="{ %string('') }")

    @cached_property
    def ytdl_sub_input_url_index(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The index of the input URL as defined in the subscription, top-most being the 0th index.
        """
        # init as -1 so if prior downloaded entries are known when they do not have this value
        # in their .info.json
        return IntegerVariable(variable_name="ytdl_sub_input_url_index", definition="{ %int(-1) }")

    @cached_property
    def ytdl_sub_input_url_count(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The total number of input URLs as defined in the subscription.
        """
        return IntegerVariable(variable_name="ytdl_sub_input_url_count", definition="{ %int(0) }")

    @cached_property
    def download_index(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The i'th entry downloaded. NOTE that this is fetched dynamically from the download
          archive.
        """
        return IntegerVariable(variable_name="download_index", definition="{ %int(1) }")

    @cached_property
    def download_index_padded6(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The download_index padded six digits
        """
        return self.download_index.to_padded_int(variable_name="download_index_padded6", pad=6)

    @cached_property
    def upload_date_index(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          The i'th entry downloaded with this upload date.
        """
        return IntegerVariable(variable_name="upload_date_index", definition="{ %int(1) }")

    @cached_property
    def upload_date_index_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The upload_date_index padded two digits
        """
        return self.upload_date_index.to_padded_int(variable_name="upload_date_index_padded", pad=2)

    @cached_property
    def upload_date_index_reversed(self: "VariableDefinitions") -> IntegerVariable:
        """
        :description:
          100 - upload_date_index
        """
        return IntegerVariable(
            variable_name="upload_date_index_reversed",
            definition=f"{{%sub(100, {self.upload_date_index.variable_name})}}",
        )

    @cached_property
    def upload_date_index_reversed_padded(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The upload_date_index padded two digits
        """
        return self.upload_date_index_reversed.to_padded_int(
            variable_name="upload_date_index_reversed_padded", pad=2
        )


class EntryVariableDefinitions(ABC):
    @cached_property
    def uid(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The entry's unique ID
        """
        return StringMetadataVariable.from_entry(metadata_key="id", variable_name="uid")

    @cached_property
    def duration(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        :description:
          The duration of the entry in seconds if it exists. Defaults to zero otherwise.
        """
        return IntegerMetadataVariable.from_entry(metadata_key="duration", default=0)

    @cached_property
    def uid_sanitized_plex(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The sanitized uid with additional sanitizing for Plex. Replaces numbers with
          fixed-width numbers so Plex does not recognize them as season or episode numbers.
        """
        return self.uid.to_sanitized_plex(variable_name="uid_sanitized_plex")

    @cached_property
    def ie_key(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The ie_key, used in legacy yt-dlp things as the 'info-extractor key'.
          If it does not exist, return ``extractor_key``
        """
        return StringMetadataVariable.from_entry(metadata_key="ie_key", default=self.extractor_key)

    @cached_property
    def extractor_key(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The yt-dlp extractor key
        """
        return StringMetadataVariable.from_entry(metadata_key="extractor_key")

    @cached_property
    def extractor(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The yt-dlp extractor name
        """
        return StringMetadataVariable.from_entry(metadata_key="extractor")

    @cached_property
    def epoch(self: "VariableDefinitions") -> IntegerMetadataVariable:
        """
        :description:
          The unix epoch of when the metadata was scraped by yt-dlp.
        """
        return IntegerMetadataVariable.from_entry(metadata_key="epoch")

    @cached_property
    def epoch_date(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The epoch's date, in YYYYMMDD format.
        """
        return StringVariable(
            variable_name="epoch_date",
            definition=f"{{%datetime_strftime({self.epoch.variable_name}, '%Y%m%d')}}",
        )

    @cached_property
    def epoch_hour(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The epoch's hour
        """
        return StringVariable(
            variable_name="epoch_hour",
            definition=f"{{%datetime_strftime({self.epoch.variable_name}, '%H')}}",
        )

    @cached_property
    def title(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The title of the entry. If a title does not exist, returns its unique ID.
        """
        return StringMetadataVariable.from_entry(metadata_key="title", default=self.uid)

    @cached_property
    def title_sanitized_plex(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The sanitized title with additional sanitizing for Plex. It replaces numbers with
          fixed-width numbers so Plex does not recognize them as season or episode numbers.
        """
        return self.title.to_sanitized_plex(variable_name="title_sanitized_plex")

    @cached_property
    def webpage_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The url to the webpage.
        """
        return StringMetadataVariable.from_entry(metadata_key="webpage_url")

    @cached_property
    def info_json_ext(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The "info.json" extension
        """
        return StringVariable(
            variable_name="info_json_ext",
            definition="info.json",
        )

    @cached_property
    def description(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The description if it exists. Otherwise, returns an emtpy string.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="description",
            default="",
        )

    @cached_property
    def uploader_id(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The uploader id if it exists, otherwise return the unique ID.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="uploader_id",
            default=self.uid,
        )

    @cached_property
    def uploader(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The uploader if it exists, otherwise return the uploader ID.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="uploader",
            default=self.uploader_id,
        )

    @cached_property
    def uploader_url(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The uploader url if it exists, otherwise returns the webpage_url.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="uploader_url",
            default=self.webpage_url,
        )

    @cached_property
    def creator(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The creator name if it exists, otherwise returns the channel.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="creator",
            default=self.channel,
        )

    @cached_property
    def channel(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The channel name if it exists, otherwise returns the uploader.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="channel",
            default=self.uploader,
        )

    @cached_property
    def channel_id(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The channel id if it exists, otherwise returns the entry uploader ID.
        """
        return StringMetadataVariable.from_entry(
            metadata_key="channel_id",
            default=self.uploader_id,
        )

    @cached_property
    def ext(self: "VariableDefinitions") -> StringMetadataVariable:
        """
        :description:
          The downloaded entry's file extension
        """
        return StringMetadataVariable.from_entry(metadata_key="ext")

    @cached_property
    def thumbnail_ext(self: "VariableDefinitions") -> StringVariable:
        """
        :description:
          The download entry's thumbnail extension. Will always return 'jpg'. Until there is a
          need to support other image types, we always convert to jpg.
        """
        return StringVariable(
            variable_name="thumbnail_ext",
            definition="jpg",
        )

    @cached_property
    def comments(self: "VariableDefinitions") -> ArrayMetadataVariable:
        """
        :description:
          Comments if they are requested
        """
        return ArrayMetadataVariable(
            metadata_key="comments", variable_name="comments", definition="{ [] }"
        )

    @cached_property
    def chapters(self: "VariableDefinitions") -> ArrayMetadataVariable:
        """
        :description:
          Chapters if they exist
        """
        return ArrayMetadataVariable(
            metadata_key="chapters", variable_name="chapters", definition="{ [] }"
        )

    @cached_property
    def sponsorblock_chapters(self: "VariableDefinitions") -> ArrayMetadataVariable:
        """
        :description:
          Sponsorblock Chapters if they are requested and exist
        """
        return ArrayMetadataVariable(
            metadata_key="sponsorblock_chapters",
            variable_name="sponsorblock_chapters",
            definition="{ [] }",
        )

    @cached_property
    def requested_subtitles(self: "VariableDefinitions") -> MapMetadataVariable:
        """
        :description:
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
    @cache
    def scripts(self) -> Dict[str, str]:
        """
        Returns all variables and their scripts in dict form
        """
        return {
            var.variable_name: var.definition
            for var in [
                getattr(self, attr)
                for attr in dir(self)
                if isinstance(getattr(self, attr), Variable)
            ]
        }

    @cache
    def injected_variables(self) -> Set[MetadataVariable]:
        """
        Returns variables that get injected in the download-stage
        """
        return {
            self.download_index,
            self.upload_date_index,
            self.comments,
            self.requested_subtitles,
            self.chapters,
            self.sponsorblock_chapters,
            self.ytdl_sub_input_url,
            self.ytdl_sub_input_url_index,
            self.ytdl_sub_input_url_count,
        }

    @cache
    def required_entry_variables(self) -> Set[MetadataVariable]:
        """
        Returns variables that the entry requires to exist
        """
        return {
            self.uid,
            self.extractor_key,
            self.epoch,
            self.webpage_url,
            self.ext,
        }

    @cache
    def default_entry_variables(self) -> Set[MetadataVariable]:
        """
        Returns variables that reside on the entry that may or may not exist,
        but have defaults
        """
        return {
            self.title,
            self.extractor,
            self.description,
            self.ie_key,
            self.uploader_id,
            self.uploader,
            self.uploader_url,
            self.upload_date,
            self.release_date,
            self.channel,
            self.creator,
            self.channel_id,
            self.duration,
            self.playlist_index,
            self.playlist_count,
            self.playlist_uid,
            self.playlist_title,
            self.playlist_uploader_id,
        }

    @cache
    def unresolvable_static_variables(self) -> Set[Variable]:
        """
        Returns variables that are not static (i.e. depend on runtime)
        """
        return {
            VARIABLES.entry_metadata,
        } | self.injected_variables()


# Singletons to use externally
VARIABLES: VariableDefinitions = VariableDefinitions()
VARIABLE_SCRIPTS: Dict[str, str] = VARIABLES.scripts()
UNRESOLVED_VARIABLES: Set[str] = {
    var.variable_name for var in VARIABLES.unresolvable_static_variables()
}

CustomFunctions.register()
