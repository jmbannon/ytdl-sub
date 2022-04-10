import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict
from typing import List

from ytdl_subscribe.entries.entry import Entry


@dataclass
class DownloadMapping:
    upload_date: str
    file_paths: List[str]


class DownloadMappings:
    def __init__(self):
        self._entry_mappings: Dict[str, DownloadMapping] = {}

    @classmethod
    def from_json(cls, file_path: str) -> "DownloadMappings":
        entry_mappings = DownloadMappings()
        entry_mappings._entry_mappings = json.load(open(file_path, "r", encoding="utf8"))
        return entry_mappings

    def to_json(self) -> str:
        return json.dumps(
            {
                uid: mapping
                for uid, mapping in sorted(
                    self._entry_mappings.items(),
                    key=lambda item: item[1]["upload_date"],
                    reverse=True,
                )
            }
        )


class DownloadArchive:
    """
    Class to handle any operations to the ytdl download archive. Try to keep it as barebones as
    possible in case of future changes.
    """

    def __init__(
        self,
    ):
        self._download_archive_lines: List[str] = []

    @classmethod
    def from_file(cls, file_path: str) -> "DownloadArchive":
        lines = open(file_path, "r", encoding="utf8").readlines()
        download_archive = DownloadArchive()
        download_archive._download_archive_lines = lines
        return download_archive


class EnhancedDownloadArchive:
    """
    Maintains ytdl's download archive file as well as create an additional mapping file to map
    ytdl ids to multiple files
    """

    def __init__(self, name: str):
        self.name = name
        self._download_archive = None
        self._download_mapping = None
        self._appended_entries: List[Entry] = []

    @property
    def download_archive_file_name(self):
        return f".ytdl-subscribe-{self.name}-download-archive.txt"

    @property
    def download_mapping_file_name(self):
        return f".ytdl-subscribe-{self.name}-download-mapping.json"

    def load(self, directory: str) -> "EnhancedDownloadArchive":
        self._download_archive = DownloadArchive.from_file(
            file_path=str(Path(directory) / self.download_archive_file_name)
        )

        self._download_mapping = DownloadMappings.from_json(
            file_path=str(Path(directory) / self.download_mapping_file_name)
        )

        return self

    # def append(self, entry: Entry, relative_file_path: str):
    #     self._appended_entries.append(
    #         EntryMapping(entry=entry, relative_file_path=relative_file_path))
    #
