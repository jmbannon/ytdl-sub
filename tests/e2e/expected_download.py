import hashlib
import os.path
from pathlib import Path
from typing import Dict


class ExpectedDownload:
    """
    To test ytdl-sub downloads work, we compare each downloaded file's md5 hash to an
    expected md5 hash defined in this class
    """

    def __init__(self, expected_md5_file_hashes: Dict[Path, str]):
        self.expected_md5_file_hashes = expected_md5_file_hashes

    def assert_files_exist(self):
        """
        Assert each expected file exists and that its respective md5 hash matches.
        """
        for path, expected_md5_hash in self.expected_md5_file_hashes.items():
            assert os.path.isfile(path), f"Expected {str(path)} to be a file but it is not"

            with open(path, "rb") as file:
                md5_hash = hashlib.md5(file.read()).hexdigest()

            assert md5_hash == expected_md5_hash, f"MD5  hash for {str(path)} does not match"
