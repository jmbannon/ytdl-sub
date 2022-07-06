import hashlib
import os.path
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

from ytdl_sub.utils.file_handler import FileMetadata


@dataclass
class ExpectedDownloadFile:
    path: Path
    md5: Optional[Union[str, List[str]]] = None
    metadata: Optional[FileMetadata] = None


class ExpectedDownloads:
    """
    To test ytdl-sub downloads work, we compare each downloaded file's md5 hash to an
    expected md5 hash defined in this class.

    If the hash value is None, only assert the file exists. If the hash value is a list,
    try all the hashes (used in case the GitHub env produces different deterministic value).
    """

    def __init__(self, expected_downloads: List[ExpectedDownloadFile]):
        self.expected_downloads = expected_downloads

    @property
    def file_count(self) -> int:
        return len(self.expected_downloads)

    def contains(self, relative_path: Path) -> bool:
        return sum(relative_path == download.path for download in self.expected_downloads) == 1

    def assert_files_exist(self, relative_directory: Path):
        """
        Assert each expected file exists and that its respective md5 hash matches.
        """
        num_files = 0
        for path in Path(relative_directory).rglob("*"):
            if path.is_file():
                num_files += 1

                relative_path = Path(*path.parts[3:])
                assert self.contains(
                    relative_path
                ), f"File {relative_path} was created but not expected"

        assert num_files == self.file_count, "Mismatch in number of created files"

        for expected_download in self.expected_downloads:
            full_path = Path(relative_directory) / expected_download.path
            assert os.path.isfile(
                full_path
            ), f"Expected {str(expected_download.path)} to be a file but it is not"

            if expected_download.md5 is None:
                continue

            with open(full_path, "rb") as file:
                md5_hash = hashlib.md5(file.read()).hexdigest()

            expected_md5_hash = expected_download.md5
            if isinstance(expected_download.md5, str):
                expected_md5_hash = [expected_download.md5]

            assert md5_hash in expected_md5_hash, (
                f"MD5  hash for {str(expected_download.path)} does not match: "
                f"{md5_hash} != {expected_md5_hash}"
            )
