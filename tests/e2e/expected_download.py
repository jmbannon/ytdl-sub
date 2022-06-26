import hashlib
import os.path
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Union


class ExpectedDownload:
    """
    To test ytdl-sub downloads work, we compare each downloaded file's md5 hash to an
    expected md5 hash defined in this class.

    If the hash value is None, only assert the file exists. If the hash value is a list,
    try all the hashes (used in case the GitHub env produces different deterministic value).
    """

    def __init__(self, expected_md5_file_hashes: Dict[Path, Optional[Union[str, List[str]]]]):
        self.expected_md5_file_hashes = expected_md5_file_hashes

    @property
    def file_count(self) -> int:
        return len(self.expected_md5_file_hashes)

    def assert_files_exist(self, relative_directory: Path):
        """
        Assert each expected file exists and that its respective md5 hash matches.
        """
        num_files = 0
        for path in Path(relative_directory).rglob("*"):
            if path.is_file():
                num_files += 1

                relative_path = Path(*path.parts[3:])
                assert (
                    relative_path in self.expected_md5_file_hashes
                ), f"File {relative_path} was created but not expected"

        assert num_files == self.file_count, "Mismatch in number of created files"

        for relative_path, expected_md5_hash in self.expected_md5_file_hashes.items():
            full_path = Path(relative_directory) / relative_path
            assert os.path.isfile(
                full_path
            ), f"Expected {str(relative_path)} to be a file but it is not"

            if expected_md5_hash is None:
                continue

            with open(full_path, "rb") as file:
                md5_hash = hashlib.md5(file.read()).hexdigest()

            if isinstance(expected_md5_hash, str):
                expected_md5_hash = [expected_md5_hash]

            assert md5_hash in expected_md5_hash, (
                f"MD5  hash for {str(relative_path)} does not match: "
                f"{md5_hash} != {expected_md5_hash}"
            )
