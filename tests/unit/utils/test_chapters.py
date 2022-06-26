import pytest

from ytdl_sub.utils.chapters import Timestamp


class TestTimestamp:
    @pytest.mark.parametrize(
        "timestamp_str, timestamp_int",
        [
            ("0:00", 0),
            ("0:24", 24),
            ("1:11", 71),
            ("01:11", 71),
            ("00:22", 22),
            ("1:01:01", 3600 + 60 + 1),
            ("01:01:01", 3600 + 60 + 1),
            ("00:00:00", 0),
        ],
    )
    def test_timestamp_from_str(self, timestamp_str, timestamp_int):
        ts = Timestamp.from_str(timestamp_str=timestamp_str)
        assert ts.timestamp_sec == timestamp_int
