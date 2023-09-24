from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from yt_dlp import match_filter_func

from ytdl_sub.config.plugin import Plugin
from ytdl_sub.config.preset_options import OptionsDictValidator
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.validators import StringListValidator

logger = Logger.get("match_filters")

_DEFAULT_DOWNLOAD_MATCH_FILTERS: List[str] = ["!is_live & !is_upcoming & !post_live"]


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

    _optional_keys = {"filters", "download_filters"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """Ensure filters looks right"""
        if isinstance(value, dict):
            value["filters"] = value.get("filters", [""])
            value["download_filters"] = value.get("download_filters", [""])
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)
        self._filters = self._validate_key_if_present(key="filters", validator=StringListValidator)
        self._download_filters = self._validate_key(
            key="download_filters",
            validator=StringListValidator,
            default=_DEFAULT_DOWNLOAD_MATCH_FILTERS,
        )

    @property
    def filters(self) -> List[str]:
        """
        The filters themselves. If used multiple times, the filter matches if at least one of the
        conditions are met. For logical AND's between match filters, use the ``&`` operator in
        a single match filter. These are applied when gathering metadata.
        """
        return [validator.value for validator in self._filters.list] if self._filters else []

    @property
    def download_filters(self) -> List[str]:
        """
        Filters to apply during the download stage. This can be useful when building presets
        that contain match-filters that you do not want to conflict with metadata-based
        match-filters since they act as logical OR's.

        By default, if no download_filters are present, then the filter
        ``"!is_live & !is_upcoming & !post_live"`` is added.
        """
        return [validator.value for validator in self._download_filters.list]


class MatchFiltersPlugin(Plugin[MatchFiltersOptions]):
    plugin_options_type = MatchFiltersOptions

    @classmethod
    def default_ytdl_options(cls) -> Dict:
        """
        Returns
        -------
        match-filter to filter out live + upcoming videos when downloading
        """
        return {
            "match_filter": match_filter_func(
                filters=[], breaking_filters=_DEFAULT_DOWNLOAD_MATCH_FILTERS
            ),
        }

    def ytdl_options_match_filters(self) -> Tuple[List[str], List[str]]:
        """
        Returns
        -------
        match_filters to apply at the metadata stage
        """
        return self.plugin_options.filters, []

    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        match_filters to apply at the download stage
        """
        return {
            "match_filter": match_filter_func(
                filters=[], breaking_filters=self.plugin_options.download_filters
            ),
        }
