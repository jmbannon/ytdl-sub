from datetime import datetime

from ytdl_sub.script.types.resolvable import Integer
from ytdl_sub.script.types.resolvable import String


class DateFunctions:
    @staticmethod
    def datetime_strftime(posix_timestamp: Integer, date_format: String) -> String:
        """
        :description:
          Converts a posix timestamp to a date using strftime formatting.
        """
        return String(datetime.utcfromtimestamp(posix_timestamp.value).strftime(date_format.value))
