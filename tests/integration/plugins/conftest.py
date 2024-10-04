import tempfile
from unittest.mock import patch

import pytest

from ytdl_sub.utils.chapters import Chapters


@pytest.fixture
def mock_chapters_class():
    with patch.object(Chapters, "from_empty") as mock_chapters:
        mock_chapters.return_value = Chapters.from_string(
            """
            "0:00 Intro\n",
            "00:07 Part 1\n",
            "0:13 Part 2\n",
            "00:19 Part 3\n",
        """
        )

        yield
