import copy
import json
import os.path
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from yt_dlp import DateRange

from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.validators.exceptions import DownloadArchiveException


@dataclass
class DownloadMapping:
    upload_date: str
    file_paths: Set[str]


class DownloadMappings:
    _strptime_format = "%Y-%m-%d"

    def __init__(self):
        self._entry_mappings: Dict[str, DownloadMapping] = {}

    @classmethod
    def from_file(cls, json_file_path: str) -> "DownloadMappings":
        entry_mappings_json = json.load(open(json_file_path, "r", encoding="utf8"))
        for uid in entry_mappings_json.keys():
            entry_mappings_json[uid] = DownloadMapping(
                upload_date=entry_mappings_json[uid]["upload_date"],
                file_paths=set(entry_mappings_json[uid]["file_paths"]),
            )

        download_mappings = DownloadMappings()
        download_mappings._entry_mappings = entry_mappings_json
        return download_mappings

    @property
    def entry_ids(self) -> List[str]:
        return list(self._entry_mappings.keys())

    def add_entry(self, entry: Entry, entry_file_path: str) -> "DownloadMappings":
        if entry.uid in self.entry_ids:
            self._entry_mappings[entry.uid].file_paths.add(entry_file_path)
        else:
            self._entry_mappings[entry.uid] = DownloadMapping(
                upload_date=entry.standardized_upload_date, file_paths={entry_file_path}
            )
        return self

    def remove_entry(self, entry_id: str) -> "DownloadMappings":
        if entry_id in self.entry_ids:
            del self._entry_mappings[entry_id]
        return self

    def get_entries_out_of_range(self, date_range: DateRange) -> Dict[str, DownloadMapping]:
        """
        :param date_range: range of dates that entries' upload dates must be within
        :return: dict of entry_id: mapping if the upload date is not in the date range
        """
        out_of_range_entry_mappings = copy.deepcopy(self._entry_mappings)
        for uid in list(out_of_range_entry_mappings.keys()):
            upload_date = datetime.strptime(
                date_string=out_of_range_entry_mappings[uid].upload_date,
                format=self._strptime_format,
            ).date()

            if upload_date in date_range:
                del out_of_range_entry_mappings[uid]

        return out_of_range_entry_mappings

    def to_file(self, output_json_file: str) -> "DownloadMappings":
        json.dump(
            obj={
                uid: mapping
                for uid, mapping in sorted(
                    self._entry_mappings.items(),
                    key=lambda item: item[1]["upload_date"],
                    reverse=True,
                )
            },
            fp=open(output_json_file, "w", encoding="utf8"),
            indent=2,
        )
        return self


class DownloadArchive:
    """
    Class to handle any operations to the ytdl download archive. Try to keep it as barebones as
    possible in case of future changes.
    """

    def __init__(self):
        self._download_archive_lines: List[str] = []

    @classmethod
    def from_file(cls, file_path: str) -> "DownloadArchive":
        lines = open(file_path, "r", encoding="utf8").readlines()
        download_archive = DownloadArchive()
        download_archive._download_archive_lines = lines
        return download_archive

    def to_file(self, file_path: str) -> "DownloadArchive":
        with open(file_path, "w", encoding="utf8") as file:
            file.writelines(self._download_archive_lines)
        return self

    def contains(self, entry_id: str) -> bool:
        return any(entry_id in line for line in self._download_archive_lines)

    def remove_entry(self, entry_id: str) -> "DownloadArchive":
        self._download_archive_lines = [
            line for line in self._download_archive_lines if entry_id not in line
        ]
        return self


class EnhancedDownloadArchive:
    """
    Maintains ytdl's download archive file as well as create an additional mapping file to map
    ytdl ids to multiple files. Used to delete 'stale' files that are out of range based on the
    file's entry's upload date.

    Should be used in this order:

    1. self.prepare_download_archive()
        Internally calls...
        a. self._load()
            - Checks the output directory to see if existing download archive/mapping files exist.
              Loads them into the class if they do. If both do not exist, do not load anything since
              they are getting instantiated for the first time. If only one archive/mapping file
              exists but not the other, error.
        b. self._copy_to_working_directory()
            - If the files were loaded successfully, copy them to the working directory. This will
              let ytdlp reuse the download archive file.
    2. ( Perform the ytdlp download using a download archive with the same name )
        - An existing archive should have been copied into the working directory for reuse
    3. self.mapping.add_entry(entry, file_path)
        - Should be called for any file created for the given entry that gets moved to the output
          directory
    4. OPTIONAL: self.remove_stale_files()
        - After all files have been moved over in the output directory, remove any stale files that
          exist in there.
    5. self.save_download_archive()
        - Save the updated archive/mapping files to the output directory.
    6. ( Delete the working directory )
    """

    def __init__(self, subscription_name: str, working_directory: str, output_directory: str):
        self.subscription_name = subscription_name
        self.working_directory = working_directory
        self.output_directory = output_directory

        self._download_archive: Optional[DownloadArchive] = None
        self._download_mapping: Optional[DownloadMappings] = None

    @property
    def _archive_file_name(self) -> str:
        """
        :return: The download archive's file name (no path)
        """
        return f".ytdl-subscribe-{self.subscription_name}-download-archive.txt"

    @property
    def _mapping_file_name(self) -> str:
        """
        :return: The download mapping's file name (no path)
        """
        return f".ytdl-subscribe-{self.subscription_name}-download-mapping.json"

    @property
    def _archive_output_file_path(self) -> str:
        """
        :return: The download archive's file path in the output directory.
        """
        return str(Path(self.output_directory) / self._archive_file_name)

    @property
    def _mapping_output_file_path(self):
        """
        :return: The download mapping's file path in the output directory.
        """
        return str(Path(self.output_directory) / self._mapping_file_name)

    @property
    def _archive_working_file_path(self) -> str:
        """
        :return: The download archive's file path in the working directory.
        """
        return str(Path(self.working_directory) / self._archive_file_name)

    @property
    def _mapping_working_file_path(self):
        """
        :return: The download mapping's file path in the working directory.
        """
        return str(Path(self.working_directory) / self._mapping_file_name)

    @property
    def mapping(self) -> DownloadMappings:
        if self._download_mapping is None:
            raise ValueError("Tried to use download mapping before it was loaded")
        return self._download_mapping

    def load(self) -> "EnhancedDownloadArchive":
        download_archive_is_file = os.path.isfile(self._mapping_output_file_path)
        download_mapping_is_file = os.path.isfile(self._archive_output_file_path)

        if download_archive_is_file ^ download_mapping_is_file:
            found_file_path, missing_name, missing_file_path = (
                (self._archive_output_file_path, "mapping", self._mapping_output_file_path)
                if download_archive_is_file
                else (self._mapping_output_file_path, "archive", self._archive_output_file_path)
            )

            raise DownloadArchiveException(
                f"Error when loading archive files for {self.subscription_name}. Partially loaded "
                f"the enhanced download archive, but is missing the {missing_name} file located at "
                f"{missing_file_path}. Either disable 'maintain_download_archive' or delete "
                f"{found_file_path} to recreate the two missing files."
            )

        # If both files exist, load them up
        if download_archive_is_file and download_mapping_is_file:
            self._download_archive = DownloadArchive.from_file(
                file_path=self._archive_output_file_path
            )
            self._download_mapping = DownloadMappings.from_file(
                json_file_path=self._mapping_output_file_path
            )
        # Otherwise, init an empty download mappings object. Keep _download_archive as None to
        # indicate it was not loaded
        else:
            self._download_mapping = DownloadMappings()

        return self

    def copy_to_working_directory(self) -> "EnhancedDownloadArchive":
        # If no download archive was found, then there is nothing to copy
        if not self._download_archive:
            return self

        shutil.copyfile(self._archive_output_file_path, self._archive_working_file_path)
        shutil.copyfile(self._mapping_output_file_path, self._mapping_working_file_path)

        return self

    def remove_stale_files(self, date_range: DateRange) -> "EnhancedDownloadArchive":
        stale_mappings: Dict[str, DownloadMapping] = self.mapping.get_entries_out_of_range(
            date_range=date_range
        )

        for uid, mapping in stale_mappings.items():
            print(f"[{uid}] Removing the following stale file(s):")
            for file_path in mapping.file_paths:
                print(f"  - {file_path}")
                if os.path.exists(file_path):
                    os.remove(file_path)

            self.mapping.remove_entry(entry_id=uid)

        return self

    def save_download_archive(self) -> "EnhancedDownloadArchive":
        # Load the download archive from the working directory, which should contain any past
        # and new entries downloaded in this session
        self._download_archive = DownloadArchive.from_file(self._archive_working_file_path)

        # Keep the download archive in sync with the mapping
        for entry_id in self.mapping.entry_ids:
            if not self._download_archive.contains(entry_id):
                self._download_archive.remove_entry(entry_id)

        # Save the archive/mappign files
        self._download_archive.to_file(file_path=self._archive_output_file_path)
        self._download_mapping.to_file(output_json_file=self._mapping_output_file_path)

        return self
