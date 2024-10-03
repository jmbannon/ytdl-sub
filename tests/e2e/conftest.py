import tempfile

import pytest

from ytdl_sub.utils.file_handler import FileHandler


@pytest.fixture
def timestamps_file_path():
    timestamps = [
        "0:00 Intro\n",
        "00:10 Part 1\n",
        "0:20 Part 2\n",
        "00:30 Part 3\n",
        "0:00:40 Part 4\n",
        "00:01:01 Part 5\n",
    ]

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".txt", delete=False
    ) as tmp:
        tmp.writelines(timestamps)

    try:
        yield tmp.name
    finally:
        FileHandler.delete(tmp.name)
