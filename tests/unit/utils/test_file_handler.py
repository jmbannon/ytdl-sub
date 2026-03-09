import pytest

from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.system import IS_WINDOWS


class TestFileHandler:

    def test_directory_exists(self):
        if IS_WINDOWS:
            return

        assert FileHandler.is_path_writable("/tmp")
        assert FileHandler.is_path_writable("/tmp/")
        assert FileHandler.is_path_writable("/tmp/non-existent")
        assert FileHandler.is_path_writable("/tmp/non-existent/")
        assert FileHandler.is_path_writable("/tmp/non-existent/nested")

        assert not FileHandler.is_path_writable("/lol-in-root")
        assert not FileHandler.is_path_writable("/")
