from typing import Dict
from typing import Optional

from ytdl_sub.entries.script.kwargs import KwargKey
from ytdl_sub.entries.script.variables import Variables

ENTRY_MAP_VARIABLE = "entry"


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


def sanitized(key: KwargKey) -> str:
    return f"{{%sanitize({key.variable_name})}}"


def sanitized_plex(key: KwargKey) -> str:
    return f"""{{
    }}"""


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
    # UID_SANITIZED
    # UID_SANITIZED_PLEX
    # title_sanitized
    # title_sanitized_plex
    # epoch_date
    # epoch_hour
    # creator
    # creator_sanitized
    # channel
    # channel_sanitized
    # channel_id
    # ext
}

ENTRY_ARCHIVE_VARIABLES: Dict[KwargKey, str] = {
    # download_index
    # download_index_padded6
    # upload_date_index
    # upload_date_index_padded
    # upload_date_index_reversed
    # upload_date_index_reversed_padded
}

ENTRY_UPLOAD_DATE_VARIABLES: Dict[KwargKey, str] = {
    # upload_date
    # upload_year
    # upload_year_truncated
    # upload_year_truncated_reversed
    # upload_month_reversed
    # upload_month_reversed_padded
    # upload_month_padded
    # upload_day_padded
    # upload_month
    # upload_day
    # upload_day_reversed
    # upload_day_reversed_padded
    # upload_day_of_year
    # upload_day_of_year_padded
    # upload_day_of_year_reversed
    # upload_day_of_year_reversed_padded
    # upload_date_standardized
}

ENTRY_RELEASE_DATE_VARIABLES: Dict[KwargKey, str] = {
    # release_date
    # release_year
    # release_year_truncated
    # release_year_truncated_reversed
    # release_month_reversed
    # release_month_reversed_padded
    # release_month_padded
    # release_day_padded
    # release_month
    # release_day
    # release_day_reversed
    # release_day_reversed_padded
    # release_day_of_year
    # release_day_of_year_padded
    # release_day_of_year_reversed
    # release_day_of_year_reversed_padded
    # release_date_standardized
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
    # source_uploader_id
    # source_uploader
    # source_uploader_url
}
