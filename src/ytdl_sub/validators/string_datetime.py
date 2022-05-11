from yt_dlp.utils import datetime_from_str

from ytdl_sub.validators.validators import Validator


class StringDatetimeValidator(Validator):
    """
    String that contains a yt-dlp datetime. From their docs:

    .. code-block:: Markdown

       A string in the format YYYYMMDD or
       (now|today|yesterday|date)[+-][0-9](microsecond|second|minute|hour|day|week|month|year)(s)

    Valid examples are ``now-2weeks`` or ``20200101``.
    """

    _expected_value_type = str
    _expected_value_type_name = "datetime string"

    def __init__(self, name, value):
        super().__init__(name, value)

        try:
            _ = datetime_from_str(self._value)
        except Exception as exc:
            raise self._validation_exception(str(exc))

    @property
    def datetime_str(self) -> str:
        """Returns the datetime as a string"""
        return self._value
