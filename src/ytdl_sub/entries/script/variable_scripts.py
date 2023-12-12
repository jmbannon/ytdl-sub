from typing import Dict
from typing import List
from typing import Optional
from typing import Set

import mergedeep

from ytdl_sub.entries.script.custom_functions import CustomFunctions
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


def _get(
    cast: str,
    metadata: Metadata,
    key: MetadataVariable,
    default: Optional[Variable | str | int | Dict | List],
) -> str:
    if default is None:
        # TODO: assert with good error message if key DNE
        out = f"%map_get({metadata.variable_name}, '{key.metadata_key}')"
    elif isinstance(default, Variable):
        out = f"%map_get_non_empty({metadata.variable_name}, '{key.metadata_key}', {default.variable_name})"
    elif isinstance(default, str):
        out = f"%map_get_non_empty({metadata.variable_name}, '{key.metadata_key}', '{default}')"
    elif isinstance(default, dict):
        out = f"%map_get_non_empty({metadata.variable_name}, '{key.metadata_key}', {{}})"
    elif isinstance(default, list):
        out = f"%map_get_non_empty({metadata.variable_name}, '{key.metadata_key}', [])"
    else:
        out = f"%map_get_non_empty({metadata.variable_name}, '{key.metadata_key}', {default})"

    return f"{{ %legacy_bracket_safety(%{cast}({out})) }}"


###############################################################################################
# Entry Getters


def entry_get_str(key: MetadataVariable, default: Optional[Variable | str] = None) -> str:
    return _get("string", metadata=v.entry_metadata, key=key, default=default)


def entry_get_int(key: MetadataVariable, default: Optional[Variable | int] = None) -> str:
    return _get("int", metadata=v.entry_metadata, key=key, default=default)


def entry_get_map(key: MetadataVariable, default: Optional[Variable | Dict] = None):
    return _get("map", metadata=v.entry_metadata, key=key, default=default)


def entry_get_array(key: MetadataVariable, default: Optional[Variable | List] = None):
    return _get("array", metadata=v.entry_metadata, key=key, default=default)


###############################################################################################
# Playlist Getters


def playlist_get_str(key: MetadataVariable, default: Optional[Variable | str] = None) -> str:
    return _get("string", metadata=v.playlist_metadata, key=key, default=default)


def playlist_get_int(key: MetadataVariable, default: Optional[Variable | int] = None) -> str:
    return _get("int", metadata=v.playlist_metadata, key=key, default=default)


###############################################################################################
# Source Getters


def source_get_str(key: MetadataVariable, default: Optional[Variable | str] = None) -> str:
    return _get("string", metadata=v.source_metadata, key=key, default=default)


def source_get_int(key: MetadataVariable, default: Optional[Variable | int] = None) -> str:
    return _get("int", metadata=v.source_metadata, key=key, default=default)


###############################################################################################
# Scripts

ENTRY_EMPTY_METADATA: Dict[Variable, str] = {v.entry_metadata: "{ {} }"}

ENTRY_HARDCODED_VARIABLES: Dict[Variable, str] = {
    v.info_json_ext: "info.json",
    v.thumbnail_ext: "jpg",
}

ENTRY_RELATIVE_VARIABLES: Dict[MetadataVariable, str] = {
    v.playlist_metadata: entry_get_map(v.playlist_metadata, {}),
    v.source_metadata: entry_get_map(v.source_metadata, {}),
    v.sibling_metadata: entry_get_array(v.sibling_metadata, []),
}

ENTRY_REQUIRED_VARIABLES: Dict[MetadataVariable, str] = {
    v.uid: entry_get_str(v.uid),
    v.extractor_key: entry_get_str(v.extractor_key),
    v.epoch: entry_get_int(v.epoch),
    v.webpage_url: entry_get_str(v.webpage_url),
    v.ext: entry_get_str(v.ext),
}

ENTRY_DEFAULT_VARIABLES: Dict[MetadataVariable, str] = {
    v.playlist_index: playlist_get_int(v.playlist_index, 1),
    v.title: entry_get_str(v.title, v.uid),
    v.extractor: entry_get_str(v.extractor, v.extractor_key),
    v.description: entry_get_str(v.description, ""),
    v.uploader_id: entry_get_str(v.uploader_id, v.uid),
    v.uploader: entry_get_str(v.uploader, v.uploader_id),
    v.uploader_url: entry_get_str(v.uploader_url, v.webpage_url),
    v.upload_date: entry_get_str(v.upload_date, v.epoch_date),
    v.release_date: entry_get_str(v.release_date, v.upload_date),
    v.channel: entry_get_str(v.channel, v.uploader),
    v.creator: entry_get_str(v.creator, v.channel),
    v.channel_id: entry_get_str(v.channel_id, v.uploader_id),
}

# MARK AS UNRESOLVABLE UNTIL THEY ARE ADDED
ENTRY_INJECTED_VARIABLES: Dict[Variable, str] = {
    v.download_index: "{%int(1)}",
    v.upload_date_index: "{%int(1)}",
    v.comments: "",
    v.requested_subtitles: "",
    v.sponsorblock_chapters: "",
    v.ytdl_sub_input_url: f"{{{v.source_webpage_url.variable_name}}}",
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
    v.playlist_uid: playlist_get_str(v.playlist_uid, v.uid),
    v.playlist_title: playlist_get_str(v.playlist_title, v.title),
    v.playlist_webpage_url: playlist_get_str(v.playlist_webpage_url, v.webpage_url),
    v.playlist_count: playlist_get_int(v.playlist_count, 1),
    v.playlist_description: playlist_get_str(v.playlist_description, v.description),
    v.playlist_uploader_id: playlist_get_str(v.playlist_uploader_id, v.uploader_id),
    v.playlist_uploader: playlist_get_str(v.playlist_uploader, v.uploader),
    v.playlist_uploader_url: playlist_get_str(v.playlist_uploader_url, v.playlist_webpage_url),
}

PLAYLIST_DERIVED_VARIABLES: Dict[Variable, str] = {
    v.playlist_title_sanitized: sanitized(v.playlist_title),
    v.playlist_index_reversed: f"{{%sub({v.playlist_count.variable_name}, {v.playlist_index.variable_name}, -1)}}",
    v.playlist_index_padded: pad_int(v.playlist_index, 2),
    v.playlist_index_reversed_padded: pad_int(v.playlist_index_reversed, 2),
    v.playlist_index_padded6: pad_int(v.playlist_index, 6),
    v.playlist_index_reversed_padded6: pad_int(v.playlist_index_reversed, 6),
    v.playlist_uploader_sanitized: sanitized(v.playlist_uploader),
}


SOURCE_VARIABLES: Dict[Variable, str] = {
    v.source_uid: source_get_str(v.source_uid, v.playlist_uid),
    v.source_title: source_get_str(v.source_title, v.playlist_title),
    v.source_webpage_url: source_get_str(v.source_webpage_url, v.playlist_webpage_url),
    v.source_index: source_get_int(v.source_index, 1),
    v.source_count: source_get_int(v.source_count, 1),
    v.source_description: source_get_str(v.source_description, v.playlist_description),
    v.source_uploader_id: source_get_str(v.source_uploader_id, v.playlist_uploader_id),
    v.source_uploader: source_get_str(v.source_uploader, v.playlist_uploader),
    v.source_uploader_url: source_get_str(v.source_uploader_url, v.source_webpage_url),
}

SOURCE_DERIVED_VARIABLES: Dict[Variable, str] = {
    v.source_title_sanitized: sanitized(v.source_title),
    v.source_index_padded: pad_int(v.source_index, 2),
}

SIBLING_VARIABLES: Dict[Variable, str] = {
    v.playlist_max_upload_date: f"""{{
        %array_reduce(
            %if_passthrough(
                %extract_field_from_siblings('{v.upload_date.variable_name}'),
                [{v.upload_date.variable_name}]
            ),
            %max
        )
    }}"""
}

SIBLING_DERIVED_VARIABLES: Dict[Variable, str] = {
    v.playlist_max_upload_year: date_metadata(v.playlist_max_upload_date, "year"),
    v.playlist_max_upload_year_truncated: date_metadata(
        v.playlist_max_upload_date, "year_truncated"
    ),
}

_VARIABLE_SCRIPTS: Dict[Variable, str] = {}
mergedeep.merge(
    _VARIABLE_SCRIPTS,
    ENTRY_EMPTY_METADATA,
    ENTRY_HARDCODED_VARIABLES,
    ENTRY_RELATIVE_VARIABLES,
    ENTRY_REQUIRED_VARIABLES,
    ENTRY_DEFAULT_VARIABLES,
    ENTRY_INJECTED_VARIABLES,
    ENTRY_DERIVED_VARIABLES,
    ENTRY_UPLOAD_DATE_VARIABLES,
    ENTRY_RELEASE_DATE_VARIABLES,
    SIBLING_VARIABLES,
    SIBLING_DERIVED_VARIABLES,
    PLAYLIST_VARIABLES,
    PLAYLIST_DERIVED_VARIABLES,
    SOURCE_VARIABLES,
    SOURCE_DERIVED_VARIABLES,
)

VARIABLE_SCRIPTS: Dict[str, str] = {
    var.variable_name: script for var, script in _VARIABLE_SCRIPTS.items()
}


def _keys(*variables: Dict[Variable, str]) -> Set[str]:
    keys: Set[str] = set()
    for variable_set in variables:
        keys.update(set(var.variable_name for var in variable_set.keys()))
    return keys


UNRESOLVED_VARIABLES: Set[str] = _keys(
    ENTRY_EMPTY_METADATA,
    ENTRY_INJECTED_VARIABLES,
)

CustomFunctions.register()
