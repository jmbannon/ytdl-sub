import json
import os.path
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Optional

from resources import RESOURCE_PATH

from ytdl_sub.utils.file_handler import get_file_md5_hash

_EXPECTED_DOWNLOADS_SUMMARY_PATH = RESOURCE_PATH / "expected_downloads_summaries"


def _get_files_in_directory(relative_directory: Path | str) -> List[Path]:
    relative_file_paths: List[Path] = []
    for path in Path(relative_directory).rglob("*"):
        if path.is_file():
            relative_path = Path(*path.parts[3:])
            relative_file_paths.append(relative_path)

    return relative_file_paths


@dataclass
class ExpectedDownloadFile:
    path: Path
    md5: str


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

    def assert_files_exist(
        self, relative_directory: str | Path, ignore_md5_hashes_for: Optional[List[str]] = None
    ):
        """
        Assert each expected file exists and that its respective md5 hash matches.
        Ignores .info.json files by default since metadata can easily change
        """
        if ignore_md5_hashes_for is None:
            ignore_md5_hashes_for = []

        relative_file_paths = _get_files_in_directory(relative_directory=relative_directory)

        for file_path in relative_file_paths:
            assert self.contains(file_path), f"File {file_path} was created but not expected"

        assert len(relative_file_paths) == self.file_count, "Mismatch in number of created files"

        for expected_download in self.expected_downloads:
            path = str(expected_download.path)
            full_path = Path(relative_directory) / path
            assert os.path.isfile(full_path), f"Expected {path} to be a file but it is not"

            if path in ignore_md5_hashes_for or path.endswith(".info.json"):
                continue

            md5_hash = get_file_md5_hash(full_file_path=full_path)
            assert md5_hash in expected_download.md5, (
                f"MD5  hash for {str(expected_download.path)} does not match: "
                f"{md5_hash} != {expected_download.md5}"
            )

    @classmethod
    def from_dict(cls, expected_downloads_dict) -> "ExpectedDownloads":
        expected_downloads: List[ExpectedDownloadFile] = []
        for file_path, md5_hash in expected_downloads_dict.items():
            expected_downloads.append(ExpectedDownloadFile(path=Path(file_path), md5=md5_hash))

        return cls(expected_downloads=expected_downloads)

    @classmethod
    def from_file(cls, file_path: str | Path) -> "ExpectedDownloads":
        with open(file_path, mode="r", encoding="utf-8") as file:
            expected_downloads_dict = json.load(file)
        return cls.from_dict(expected_downloads_dict)

    @classmethod
    def from_directory(cls, directory_path: str | Path) -> "ExpectedDownloads":
        relative_file_paths = _get_files_in_directory(relative_directory=directory_path)
        expected_downloads_dict = {
            str(file_path): get_file_md5_hash(full_file_path=Path(directory_path) / file_path)
            for file_path in relative_file_paths
        }
        return cls.from_dict(expected_downloads_dict)

    def to_summary_file(self, summary_file_path: Path | str) -> None:
        expected_downloads_dict = {
            str(exp_dl.path): exp_dl.md5 for exp_dl in self.expected_downloads
        }

        with open(summary_file_path, mode="w", encoding="utf-8") as file:
            json.dump(
                obj=expected_downloads_dict, fp=file, sort_keys=True, ensure_ascii=False, indent=2
            )


def assert_expected_downloads(
    output_directory: str | Path,
    dry_run: bool,
    expected_download_summary_file_name: str,
    ignore_md5_hashes_for: Optional[List[str]] = None,
    regenerate_expected_download_summary: bool = True,
):
    if dry_run:
        output_directory_contents = list(Path(output_directory).rglob("*"))
        assert (
            len(output_directory_contents) == 0
        ), f"Expected output directory to be empty after a dry-run, but found {output_directory_contents}"
        return

    summary_full_path = _EXPECTED_DOWNLOADS_SUMMARY_PATH / expected_download_summary_file_name
    if regenerate_expected_download_summary:
        os.makedirs(os.path.dirname(summary_full_path), exist_ok=True)
        ExpectedDownloads.from_directory(directory_path=output_directory).to_summary_file(
            summary_file_path=summary_full_path
        )

    ExpectedDownloads.from_file(summary_full_path).assert_files_exist(
        relative_directory=output_directory, ignore_md5_hashes_for=ignore_md5_hashes_for
    )
