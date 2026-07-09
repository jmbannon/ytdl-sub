from typing import Set

from ytdl_sub.validators.string_select_validator import OverridesStringSelectValidator


class KeepMaxFilesSortByValidator(OverridesStringSelectValidator):
    _select_values: Set[str] = {"upload_date", "playlist_index_asc", "playlist_index_desc"}
