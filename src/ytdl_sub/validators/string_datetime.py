from yt_dlp.utils import datetime_from_str

from ytdl_sub.validators.validators import Validator


class StringDatetimeValidator(Validator):
    """
    Validates a ytdl datetime string value
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
