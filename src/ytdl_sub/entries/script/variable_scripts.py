from typing import Dict
from typing import Optional
from typing import Set

import mergedeep

from ytdl_sub.entries.script.function_scripts import CustomFunctions
from ytdl_sub.entries.script.variable_definitions import VARIABLES as v
from ytdl_sub.entries.script.variable_definitions import Metadata
from ytdl_sub.entries.script.variable_definitions import MetadataVariable
from ytdl_sub.entries.script.variable_definitions import Variable

###############################################################################################
# Helpers


def pad_int(key: Variable, pad: int) -> str:
    return f"{{%pad_zero({key.variable_name}, {pad})}}"


def sanitized(key: Variable) -> str:
    return f"{{%sanitize({key.variable_name})}}"


def sanitized_plex(key: Variable) -> str:
    return f"{{%sanitize_plex_episode({key.variable_name})}}"


def date_metadata(date_key: Variable, metadata_key: str) -> str:
    return f"{{%map_get(%to_date_metadata({date_key.variable_name}), '{metadata_key}')}}"


###############################################################################################
# Metadata Getters


def _get_internal(
    metadata: Metadata, key: MetadataVariable, default: Optional[Variable | str | int]
) -> str:
    if default is None:
        # TODO: assert with good error message if key DNE
        out = f"%map_get({metadata.variable_name}, '{key.metadata_key}')"
    elif isinstance(default, Variable):
        out = f"%map_get_non_empty({metadata.variable_name}, '{key.metadata_key}', {default.variable_name})"
    elif isinstance(default, str):
        out = f"%map_get_non_empty({metadata.variable_name}, '{key.metadata_key}', '{default}')"
    else:
        out = f"%map_get_non_empty({metadata.variable_name}, '{key.metadata_key}', {default})"

    return f"%legacy_bracket_safety({out})"


def _get_int(
    metadata: Metadata, key: MetadataVariable, default: Optional[Variable | int] = None
) -> str:
    return f"{{%int({_get_internal(metadata=metadata, key=key, default=default)})}}"


def _get(metadata: Metadata, key: MetadataVariable, default: Optional[Variable | str | int]) -> str:
    return f"{{{_get_internal(metadata=metadata, key=key, default=default)}}}"


###############################################################################################
# Entry Getters


def entry_get(key: MetadataVariable, default: Optional[Variable | str | int] = None) -> str:
    return _get(metadata=v.entry_metadata, key=key, default=default)


def entry_get_int(key: MetadataVariable, default: Optional[Variable | int] = None) -> str:
    return _get_int(metadata=v.entry_metadata, key=key, default=default)


###############################################################################################
# Playlist Getters


def playlist_get(key: MetadataVariable, default: Optional[Variable | str | int] = None) -> str:
    return _get(metadata=v.entry_metadata, key=key, default=default)


def playlist_get_int(key: MetadataVariable, default: Optional[Variable | int] = None) -> str:
    return _get_int(metadata=v.entry_metadata, key=key, default=default)


###############################################################################################
# Source Getters


def source_get(key: MetadataVariable, default: Optional[Variable | str | int] = None) -> str:
    return _get(metadata=v.entry_metadata, key=key, default=default)


def source_get_int(key: MetadataVariable, default: Optional[Variable | int] = None) -> str:
    return _get_int(metadata=v.entry_metadata, key=key, default=default)


###############################################################################################
# Scripts

ENTRY_EMPTY_METADATA: Dict[Variable, str] = {v.entry_metadata: "{ {} }"}

ENTRY_HARDCODED_VARIABLES: Dict[Variable, str] = {
    v.info_json_ext: "info.json",
    v.thumbnail_ext: "jpg",
}

ENTRY_REQUIRED_VARIABLES: Dict[MetadataVariable, str] = {
    v.uid: entry_get(v.uid),
    v.extractor_key: entry_get(v.extractor_key),
    v.epoch: entry_get_int(v.epoch),
    v.webpage_url: entry_get(v.webpage_url),
    v.ext: entry_get(v.ext),
}

ENTRY_DEFAULT_VARIABLES: Dict[MetadataVariable, str] = {
    v.playlist_index: playlist_get_int(v.playlist_index, 1),
    v.title: entry_get(v.title, v.uid),
    v.extractor: entry_get(v.extractor, v.extractor_key),
    v.description: entry_get(v.description, ""),
    v.uploader_id: entry_get(v.uploader_id, v.uid),
    v.uploader: entry_get(v.uploader, v.uploader_id),
    v.uploader_url: entry_get(v.uploader_url, v.webpage_url),
    v.upload_date: entry_get(v.upload_date, v.epoch_date),
    v.release_date: entry_get(v.release_date, v.upload_date),
    v.channel: entry_get(v.channel, v.uploader),
    v.creator: entry_get(v.creator, v.channel),
    v.channel_id: entry_get(v.channel_id, v.uploader_id),
}

# TODO: MARK AS UNRESOLVABLE UNTIL THEY ARE ADDED
ENTRY_INJECTED_VARIABLES: Dict[Variable, str] = {
    v.download_index: "{%int(1)}",
    v.upload_date_index: "{%int(1)}",
    v.playlist_max_upload_year: f"{{{v.upload_year.variable_name}}}",
}

ENTRY_DERIVED_VARIABLES: Dict[Variable, str] = {
    v.uid_sanitized: sanitized(v.uid),
    v.uid_sanitized_plex: sanitized_plex(v.uid),
    v.title_sanitized: sanitized(v.title),
    v.title_sanitized_plex: sanitized_plex(v.title),
    v.epoch_date: f"{{%datetime_strftime({v.epoch.variable_name}, '%Y%m%d')}}",
    v.epoch_hour: f"{{%datetime_strftime({v.epoch.variable_name}, '%H')}}",
    v.channel_sanitized: sanitized(v.channel),
    v.creator_sanitized: sanitized(v.creator),
    v.download_index_padded6: pad_int(v.download_index, 6),
    v.upload_date_index_padded: pad_int(v.upload_date_index, 2),
    v.upload_date_index_reversed: f"{{%sub(100, {v.upload_date_index.variable_name})}}",
    v.upload_date_index_reversed_padded: pad_int(v.upload_date_index_reversed, 2),
}

ENTRY_UPLOAD_DATE_VARIABLES: Dict[Variable, str] = {
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

ENTRY_RELEASE_DATE_VARIABLES: Dict[Variable, str] = {
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

PLAYLIST_VARIABLES: Dict[Variable, str] = {
    v.playlist_uid: playlist_get(v.playlist_uid, v.uid),
    v.playlist_title: playlist_get(v.playlist_title, v.title),
    v.playlist_webpage_url: playlist_get(v.playlist_webpage_url, v.webpage_url),
    v.playlist_count: playlist_get_int(v.playlist_count, 1),
    v.playlist_description: playlist_get(v.playlist_description, v.description),
    v.playlist_uploader_id: playlist_get(v.playlist_uploader_id, v.uploader_id),
    v.playlist_uploader: playlist_get(v.playlist_uploader, v.uploader),
    v.playlist_uploader_url: playlist_get(v.playlist_uploader_url, v.playlist_webpage_url),
}

PLAYLIST_DERIVED_VARIABLES: Dict[Variable, str] = {
    v.playlist_title_sanitized: sanitized(v.playlist_title),
    v.playlist_index_reversed: f"{{%sub({v.playlist_count.variable_name}, {v.playlist_index.variable_name}, -1)}}",
    v.playlist_index_padded: pad_int(v.playlist_index, 2),
    v.playlist_index_reversed_padded: pad_int(v.playlist_index_reversed, 2),
    v.playlist_index_padded6: pad_int(v.playlist_index, 6),
    v.playlist_index_reversed_padded6: pad_int(v.playlist_index_reversed, 6),
    v.playlist_uploader_sanitized: sanitized(v.playlist_uploader),
    v.playlist_max_upload_year_truncated: f"{{%int(%slice(%string({v.playlist_max_upload_year.variable_name}), 2))}}",
}


SOURCE_VARIABLES: Dict[Variable, str] = {
    v.source_uid: source_get(v.source_uid, v.playlist_uid),
    v.source_title: source_get(v.source_title, v.playlist_title),
    v.source_webpage_url: source_get(v.source_webpage_url, v.playlist_webpage_url),
    v.source_index: source_get_int(v.source_index, 1),
    v.source_count: source_get_int(v.source_count, 1),
    v.source_description: source_get(v.source_description, v.playlist_description),
    v.source_uploader_id: source_get(v.source_uploader_id, v.playlist_uploader_id),
    v.source_uploader: source_get(v.source_uploader, v.playlist_uploader),
    v.source_uploader_url: source_get(v.source_uploader_url, v.source_webpage_url),
}

SOURCE_DERIVED_VARIABLES: Dict[Variable, str] = {
    v.source_title_sanitized: sanitized(v.source_title),
    v.source_index_padded: pad_int(v.source_index, 2),
}

_VARIABLE_SCRIPTS: Dict[Variable, str] = {}
mergedeep.merge(
    _VARIABLE_SCRIPTS,
    ENTRY_EMPTY_METADATA,
    ENTRY_HARDCODED_VARIABLES,
    ENTRY_REQUIRED_VARIABLES,
    ENTRY_DEFAULT_VARIABLES,
    ENTRY_INJECTED_VARIABLES,
    ENTRY_DERIVED_VARIABLES,
    ENTRY_UPLOAD_DATE_VARIABLES,
    ENTRY_RELEASE_DATE_VARIABLES,
    PLAYLIST_VARIABLES,
    PLAYLIST_DERIVED_VARIABLES,
    SOURCE_VARIABLES,
    SOURCE_DERIVED_VARIABLES,
)

VARIABLE_SCRIPTS: Dict[str, str] = {
    var.variable_name: script for var, script in _VARIABLE_SCRIPTS.items()
}
UNRESOLVED_VARIABLES: Set[str] = {var.variable_name for var in ENTRY_INJECTED_VARIABLES}

CustomFunctions.register()
