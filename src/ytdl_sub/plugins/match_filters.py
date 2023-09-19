from typing import Any
from typing import List
from typing import Tuple

from ytdl_sub.config.plugin import Plugin
from ytdl_sub.config.preset_options import OptionsDictValidator
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.validators import StringListValidator

logger = Logger.get("match_filters")


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

    _required_keys = {"filters"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """Ensure filters looks right"""
        if isinstance(value, dict):
            value["filters"] = value.get("filters", [""])
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)
        self._filters = self._validate_key(key="filters", validator=StringListValidator).list

    @property
    def filters(self) -> List[str]:
        """
        The filters themselves. If used multiple times, the filter matches if at least one of the
        conditions are met. For logical AND's between match filters, use the ``&`` operator in
        a single match filter.
        """
        return [validator.value for validator in self._filters]


class MatchFiltersPlugin(Plugin[MatchFiltersOptions]):
    plugin_options_type = MatchFiltersOptions

    def ytdl_options_match_filters(self) -> Tuple[List[str], List[str]]:
        """
        Returns
        -------
        match_filter after calling the utility function for it
        """
        match_filters: List[str] = []
        for filter_str in self.plugin_options.filters:
            match_filters.append(filter_str)

        return match_filters, []
