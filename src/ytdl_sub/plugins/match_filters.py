import copy
from typing import Any
from typing import List
from typing import Tuple

from ytdl_sub.config.plugin import Plugin
from ytdl_sub.config.preset_options import OptionsDictValidator
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.validators import StringListValidator

logger = Logger.get("match_filters")


def default_filters() -> Tuple[List[str], List[str]]:
    """
    Returns
    -------
    Default filters and breaking filters to always use
    """
    return ["!is_live & !is_upcoming & !post_live"], []


def combine_filters(filters: List[str], to_combine: List[str]) -> List[str]:
    """
    Parameters
    ----------
    filters
        User-defined match-filters
    to_combine
        Filters that need to be combined via AND to the original filters.
        These are derived from plugins

    Returns
    -------
    merged filters

    Raises
    ------
    ValueError
        Only supports combining 1 filter at this time. Should never be hit by users
    """
    if len(to_combine) == 0:
        return filters
    if not filters:
        return copy.deepcopy(to_combine)

    if len(to_combine) > 1:
        raise ValueError("Match-filters to combine only supports 1 at this time")

    output_filters: List[str] = []
    filter_to_combine: str = to_combine[0]

    for match_filter in filters:
        output_filters.append(f"{match_filter} & {filter_to_combine}")

    return output_filters


class MatchFiltersOptions(OptionsDictValidator):
    """
    Set ``--match-filters``` to pass into yt-dlp to filter entries from being downloaded.
    Uses the same syntax as yt-dlp.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           match_filters:
             filters: "original_url!*=/shorts/"

    Supports one or multiple filters:

    .. code-block:: yaml

       presets:
         my_example_preset:
           match_filters:
             filters:
               - "age_limit<?18"
               - "like_count>?100"
               # Other common match-filters
               # - "original_url!*=/shorts/ & !is_live"
               # - "age_limit<?18"
               # - "availability=?public"
    """

    _optional_keys = {"filters"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """Ensure filters looks right"""
        if isinstance(value, dict):
            value["filters"] = value.get("filters", [""])
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)
        self._filters = self._validate_key_if_present(key="filters", validator=StringListValidator)

    @property
    def filters(self) -> List[str]:
        """
        The filters themselves. If used multiple times, the filter matches if at least one of the
        conditions are met. For logical AND's between match filters, use the ``&`` operator in
        a single match filter. These are applied when gathering metadata.
        """
        return [validator.value for validator in self._filters.list] if self._filters else []


class MatchFiltersPlugin(Plugin[MatchFiltersOptions]):
    plugin_options_type = MatchFiltersOptions

    def ytdl_options_match_filters(self) -> Tuple[List[str], List[str]]:
        """
        Returns
        -------
        match_filters to apply at the metadata stage
        """
        return self.plugin_options.filters, []
