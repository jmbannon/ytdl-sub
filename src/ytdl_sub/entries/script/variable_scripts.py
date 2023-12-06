from typing import Dict
from typing import Optional

from ytdl_sub.entries.script.variable_definitions import KwargKey
from ytdl_sub.entries.script.variable_definitions import Variables

ENTRY_MAP_VARIABLE = "entry_metadata"
PLAYLIST_MAP_VARIABLE = "playlist_metadata"
SOURCE_MAP_VARIABLE = "source_metadata"


def _entry_get(key: KwargKey, default: Optional[KwargKey | str | int]) -> str:
    if default is None:
        # TODO: assert with good error message if key DNE
        return f"%map_get({ENTRY_MAP_VARIABLE}, '{key.entry_key}')"
    if isinstance(default, KwargKey):
        return f"%map_get({ENTRY_MAP_VARIABLE}, '{key.entry_key}', {default.variable_name})"
    if isinstance(default, str):
        return f"%map_get({ENTRY_MAP_VARIABLE}, '{key.entry_key}', '{default}')"

    return f"%map_get({ENTRY_MAP_VARIABLE}, '{key.entry_key}', {default})"


def entry_get(key: KwargKey, default: Optional[KwargKey | str | int] = None) -> str:
    return f"{{{_entry_get(key=key, default=default)}}}"


def entry_get_int(key: KwargKey, default: Optional[KwargKey] = None) -> str:
    return f"{{%int({_entry_get(key=key, default=default)}}}"


def pad_int(key: KwargKey, pad: int) -> str:
    return f"{{%pad_zero({key.variable_name}, {pad})}}"


def sanitized(key: KwargKey) -> str:
    return f"{{%sanitize({key.variable_name})}}"


def sanitized_plex(key: KwargKey) -> str:
    return f"{{%sanitize_plex_episode({key.variable_name})}}"


def date_metadata(date_key: KwargKey, metadata_key: str) -> str:
    return f"{{%map_get(%date_metadata({date_key.variable_name}), '{metadata_key}')}}"


# singleton to produce variable keys
v = Variables()


ENTRY_HARDCODED_VARIABLES: Dict[KwargKey, str] = {
    v.info_json_ext: "info.json",
    v.thumbnail_ext: "jpg",
}

ENTRY_REQUIRED_VARIABLES: Dict[KwargKey, str] = {
    v.uid: entry_get(v.uid),
    v.ie_key: entry_get(v.ie_key),
    v.epoch: entry_get_int(v.epoch),
    v.webpage_url: entry_get(v.webpage_url),
    v.ext: entry_get(v.ext),
}

ENTRY_DEFAULT_VARIABLES: Dict[KwargKey, str] = {
    v.title: entry_get(v.title, v.uid),
    v.extractor: entry_get(v.extractor, v.ie_key),
    v.description: entry_get(v.description, ""),
    v.uploader_id: entry_get(v.uploader_id, v.uid),
    v.uploader: entry_get(v.uploader, v.uploader_id),
    v.uploader_url: entry_get(v.uploader_url, v.webpage_url),
}

ENTRY_DERIVED_VARIABLES: Dict[KwargKey, str] = {
    v.uid_sanitized: sanitized(v.uid),
    v.uid_sanitized_plex: sanitized_plex(v.uid_sanitized_plex),
    v.title_sanitized: sanitized(v.title),
    v.title_sanitized_plex: sanitized_plex(v.title),
    v.epoch_date: f"{{%datetime_strftime({v.epoch.variable_name}, '%Y%m%d')}}",
    v.epoch_hour: f"{{%datetime_strftime({v.epoch.variable_name}, '%H')}}",
    v.upload_date: entry_get(v.upload_date, v.epoch_date),
    v.release_date: entry_get(v.release_date, v.upload_date),
    v.channel: entry_get(v.channel, v.uploader),
    v.channel_sanitized: sanitized(v.channel),
    v.creator: entry_get(v.creator, v.channel),
    v.creator_sanitized: sanitized(v.creator),
    v.channel_id: entry_get(v.channel_id, v.uploader_id),
}

ENTRY_ARCHIVE_VARIABLES: Dict[KwargKey, str] = {
    v.download_index: entry_get_int(v.download_index),
    v.download_index_padded6: pad_int(v.download_index, 6),
    v.upload_date_index: entry_get_int(v.upload_date_index),
    v.upload_date_index_padded: pad_int(v.upload_date_index, 2),
    v.upload_date_index_reversed: f"{{%sub(100, {v.download_index})}}",
    v.upload_date_index_reversed_padded: pad_int(v.upload_date_index_reversed, 2),
}

ENTRY_UPLOAD_DATE_VARIABLES: Dict[KwargKey, str] = {
    v.upload_year: date_metadata(v.upload_date, "year"),
    v.upload_year_truncated: date_metadata(v.upload_date, "year_truncated"),
    v.upload_year_truncated_reversed: date_metadata(v.upload_date, "year_truncated_reversed"),
    v.upload_month_reversed: date_metadata(v.upload_date, "month_reversed"),
    v.upload_month_reversed_padded: date_metadata(v.upload_date, "month_reversed_padded"),
    v.upload_month_padded: date_metadata(v.upload_date, "month_padded"),
    v.upload_day_padded: date_metadata(v.upload_date, "day_padded"),
    v.upload_month: date_metadata(v.upload_date, "month"),
    v.upload_day: date_metadata(v.upload_date, "day"),
    v.upload_day_reversed: date_metadata(v.upload_date, "day_reversed"),
    v.upload_day_reversed_padded: date_metadata(v.upload_date, "day_reversed_padded"),
    v.upload_day_of_year: date_metadata(v.upload_date, "day_of_year"),
    v.upload_day_of_year_padded: date_metadata(v.upload_date, "day_of_year_padded"),
    v.upload_day_of_year_reversed: date_metadata(v.upload_date, "day_of_year_reversed"),
    v.upload_day_of_year_reversed_padded: date_metadata(
        v.upload_date, "day_of_year_reversed_padded"
    ),
    v.upload_date_standardized: date_metadata(v.upload_date, "date_standardized"),
}

ENTRY_RELEASE_DATE_VARIABLES: Dict[KwargKey, str] = {
    v.release_year: date_metadata(v.release_date, "year"),
    v.release_year_truncated: date_metadata(v.release_date, "year_truncated"),
    v.release_year_truncated_reversed: date_metadata(v.release_date, "year_truncated_reversed"),
    v.release_month_reversed: date_metadata(v.release_date, "month_reversed"),
    v.release_month_reversed_padded: date_metadata(v.release_date, "month_reversed_padded"),
    v.release_month_padded: date_metadata(v.release_date, "month_padded"),
    v.release_day_padded: date_metadata(v.release_date, "day_padded"),
    v.release_month: date_metadata(v.release_date, "month"),
    v.release_day: date_metadata(v.release_date, "day"),
    v.release_day_reversed: date_metadata(v.release_date, "day_reversed"),
    v.release_day_reversed_padded: date_metadata(v.release_date, "day_reversed_padded"),
    v.release_day_of_year: date_metadata(v.release_date, "day_of_year"),
    v.release_day_of_year_padded: date_metadata(v.release_date, "day_of_year_padded"),
    v.release_day_of_year_reversed: date_metadata(v.release_date, "day_of_year_reversed"),
    v.release_day_of_year_reversed_padded: date_metadata(
        v.release_date, "day_of_year_reversed_padded"
    ),
    v.release_date_standardized: date_metadata(v.release_date, "date_standardized"),
}

ENTRY_SOURCE_VARIABLES: Dict[KwargKey, str] = {
    # source_title
    # source_title_sanitized
    # source_uid
    # source_index
    # source_index_padded
    # source_count
    # source_webpage_url
    # source_description
    # source_uploader_id
    # source_uploader
    # source_uploader_url
}

ENTRY_PLAYLIST_VARIABLES: Dict[KwargKey, str] = {
    # playlist_uid
    # playlist_title
    # playlist_title_sanitized
    # playlist_index
    # playlist_index_reversed
    # playlist_index_padded
    # playlist_index_reversed_padded
    # playlist_index_padded6
    # playlist_index_reversed_padded6
    # playlist_count
    # playlist_description
    # playlist_webpage_url
    # playlist_max_upload_year
    # playlist_max_upload_year_truncated
    # playlist_uploader_id
    # playlist_uploader
    # playlist_uploader_sanitized
    # playlist_uploader_url
}
