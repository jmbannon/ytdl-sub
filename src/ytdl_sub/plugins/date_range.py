from typing import Dict
from typing import Optional

from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.datetime import to_date_range
from ytdl_sub.validators.string_datetime import StringDatetimeValidator


class DateRangeOptions(PluginOptions):
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

    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        YTDL options for setting a date range
        """
        ytdl_options_builder = YTDLOptionsBuilder()

        source_date_range = to_date_range(
            before=self.plugin_options.before,
            after=self.plugin_options.after,
            overrides=self.overrides,
        )
        if source_date_range:
            ytdl_options_builder.add({"daterange": source_date_range})

            # Only add break_on_reject if after is specified, but not before.
            # Otherwise, it can break on first metadata pull if it's after the 'before'
            if self.plugin_options.after and not self.plugin_options.before:
                ytdl_options_builder.add({"break_on_reject": True})

        return ytdl_options_builder.to_dict()
