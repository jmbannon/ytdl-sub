from datetime import datetime, timezone

from ytdl_sub.script.types.resolvable import Integer, String


class DateFunctions:
    @staticmethod
    def datetime_strftime(posix_timestamp: Integer, date_format: String) -> String:
        """
        :description:
          Converts a posix timestamp to a date using strftime formatting.
        """
        # `datetime.utcfromtimestamp` is deprecated since Python 3.12. Use the
        # timezone-aware equivalent and strip tzinfo to keep a naive UTC
        # datetime, so the strftime output is unchanged.
        utc_datetime = datetime.fromtimestamp(posix_timestamp.value, timezone.utc)
        return String(utc_datetime.replace(tzinfo=None).strftime(date_format.value))
