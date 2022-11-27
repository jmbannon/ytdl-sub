from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from yt_dlp import match_filter_func

from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.validators import StringListValidator

logger = Logger.get("match_filters")


class MatchFiltersOptions(PluginOptions):
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
               - "original_url!*=/shorts/"
               - "!is_live"
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
        conditions are met.
        """
        return [validator.value for validator in self._filters]


class MatchFiltersPlugin(Plugin[MatchFiltersOptions]):
    plugin_options_type = MatchFiltersOptions

    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        match_filter after calling the utility function for it
        """
        match_filters: List[str] = []
        for filter_str in self.plugin_options.filters:
            logger.debug("Adding match-filter %s", filter_str)
            match_filters.append(filter_str)

        return {"match_filter": match_filter_func(match_filters)}
