from typing import Dict

from yt_dlp.utils import datetime_from_str

from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator


class StringDatetimeValidator(OverridesStringFormatterValidator):
    """
    String that contains a yt-dlp datetime. From their docs:

    .. code-block:: Markdown

       A string in the format YYYYMMDD or
       (now|today|yesterday|date)[+-][0-9](microsecond|second|minute|hour|day|week|month|year)(s)

    Valid examples are ``now-2weeks`` or ``20200101``. Can use override variables in this.
    Note that yt-dlp will round times to the closest day, meaning that `day` is the lowest
    granularity possible.
    """

    _expected_value_type_name = "datetime string"

    def apply_formatter(self, variable_dict: Dict[str, str]) -> str:
        output = super().apply_formatter(variable_dict)
        try:
            _ = datetime_from_str(output)
        except Exception as exc:
            raise self._validation_exception(f"Invalid datetime string: {str(exc)}")
        return output
