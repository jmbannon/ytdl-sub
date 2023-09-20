from typing import List
from typing import Optional
from typing import Tuple

from ytdl_sub.config.plugin import Plugin
from ytdl_sub.config.preset_options import OptionsDictValidator
from ytdl_sub.utils.datetime import to_date_str
from ytdl_sub.validators.string_datetime import StringDatetimeValidator


class DateRangeOptions(OptionsDictValidator):
    """
    Only download files uploaded within the specified date range.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           date_range:
             before: "now"
             after: "today-2weeks"
    """

    _optional_keys = {"before", "after"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._before = self._validate_key_if_present("before", StringDatetimeValidator)
        self._after = self._validate_key_if_present("after", StringDatetimeValidator)

    @property
    def before(self) -> Optional[StringDatetimeValidator]:
        """
        Optional. Only download videos before this datetime.
        """
        return self._before

    @property
    def after(self) -> Optional[StringDatetimeValidator]:
        """
        Optional. Only download videos after this datetime.
        """
        return self._after


class DateRangePlugin(Plugin[DateRangeOptions]):
    plugin_options_type = DateRangeOptions

    def ytdl_options_match_filters(self) -> Tuple[List[str], List[str]]:
        """
        Returns
        -------
        match filters for before (non-breaking) and after (breaking)
        """
        match_filters: List[str] = []
        breaking_match_filters: List[str] = []

        if self.plugin_options.before:
            before_str = to_date_str(
                date_validator=self.plugin_options.before, overrides=self.overrides
            )
            match_filters.append(f"upload_date < {before_str}")

        if self.plugin_options.after:
            after_str = to_date_str(
                date_validator=self.plugin_options.after, overrides=self.overrides
            )
            breaking_match_filters.append(f"upload_date >= {after_str}")

        return match_filters, breaking_match_filters
