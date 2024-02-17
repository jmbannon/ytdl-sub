from typing import List
from typing import Optional
from typing import Tuple

from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.validators.options import ToggleableOptionsDictValidator
from ytdl_sub.utils.datetime import to_date_str
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.validators.string_datetime import StringDatetimeValidator
from ytdl_sub.validators.string_formatter_validators import OverridesBooleanFormatterValidator


class DateRangeOptions(ToggleableOptionsDictValidator):
    """
    Only download files uploaded within the specified date range.
    Dates must adhere to a yt-dlp datetime. From their docs:

    .. code-block:: Markdown

       A string in the format YYYYMMDD or
       (now|today|yesterday|date)[+-][0-9](microsecond|second|minute|hour|day|week|month|year)(s)

    Valid examples are ``now-2weeks`` or ``20200101``. Can use override variables in this.
    Note that yt-dlp will round times to the closest day, meaning that `day` is the lowest
    granularity possible.

    :Usage:

    .. code-block:: yaml

       date_range:
         before: "now"
         after: "today-2weeks"
    """

    _optional_keys = {"enable", "before", "after", "breaks"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._before = self._validate_key_if_present("before", StringDatetimeValidator)
        self._after = self._validate_key_if_present("after", StringDatetimeValidator)
        self._breaks = self._validate_key_if_present(
            "breaks", OverridesBooleanFormatterValidator, default="True"
        )

    @property
    def before(self) -> Optional[StringDatetimeValidator]:
        """
        :expected type: Optional[OverridesFormatter]
        :description:
          Only download videos before this datetime.
        """
        return self._before

    @property
    def after(self) -> Optional[StringDatetimeValidator]:
        """
        :expected type: Optional[OverridesFormatter]
        :description:
          Only download videos after this datetime.
        """
        return self._after

    @property
    def breaks(self) -> OverridesBooleanFormatterValidator:
        """
        :expected type: Optional[OverridesFormatter]
        :description:
          Toggle to enable breaking subsequent metadata downloads if an entry's upload date
          is out of range. Defaults to True.
        """
        return self._breaks


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
            after_filter = f"upload_date >= {after_str}"
            if ScriptUtils.bool_formatter_output(
                self.overrides.apply_formatter(self.plugin_options.breaks)
            ):
                breaking_match_filters.append(after_filter)
            else:
                match_filters.append(after_filter)

        return match_filters, breaking_match_filters
