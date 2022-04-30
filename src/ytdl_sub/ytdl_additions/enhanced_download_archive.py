import copy
import json
import os.path
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from yt_dlp import DateRange

from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.logger import Logger


@dataclass
class DownloadMapping:
    upload_date: str
    extractor: str
    file_names: Set[str]

    @property
    def dict(self) -> Dict[str, Any]:
        """
        :return: DownloadMapping as a dict that is serializable
        """
        return {
            "upload_date": self.upload_date,
            "extractor": self.extractor,
            "file_names": sorted(list(self.file_names)),
        }

    @classmethod
    def from_dict(cls, mapping_dict: dict) -> "DownloadMapping":
        """
        Parameters
        ----------
        mapping_dict
            Download mapping in dict format

        Returns
        -------
        Instantiated DownloadMapping class
        """
        return DownloadMapping(
            upload_date=mapping_dict["upload_date"],
            extractor=mapping_dict["extractor"],
            file_names=set(mapping_dict["file_names"]),
        )

    @classmethod
    def from_entry(cls, entry: Entry) -> "DownloadMapping":
        """
        Parameters
        ----------
        entry
            Entry to create a download mapping for

        Returns
        -------
        DownloadMapping for the entry
        """
        return DownloadMapping(
            upload_date=entry.upload_date_standardized,
            extractor=entry.extractor,
            file_names=set(),
        )


class DownloadArchive:
    """
    Class to handle any operations to the ytdl download archive. Try to keep it as barebones as
    possible in case of future changes.
    """

    def __init__(self, download_archive_lines: List[str]):
        """
        Parameters
        ----------
        download_archive_lines
            Lines found in a YTDL download archive file, i.e. youtube id-32342343423
        """
        self._download_archive_lines = download_archive_lines

    @classmethod
    def from_file(cls, file_path: str) -> "DownloadArchive":
        """
        Parameters
        ----------
        file_path
            Path to a download archive file

        Returns
        -------
        Instantiated DownloadArchive class
        """
        with open(file_path, "r", encoding="utf8") as file:
            return cls(download_archive_lines=file.readlines())

    def to_file(self, file_path: str) -> "DownloadArchive":
        """
        Parameters
        ----------
        file_path
            File path to store this download archive to

        Returns
        -------
        self
        """
        with open(file_path, "w", encoding="utf8") as file:
            for line in self._download_archive_lines:
                file.write(f"{line}\n")
        return self

    def contains(self, entry_id: str) -> bool:
        """
        Parameters
        ----------
        entry_id
            Id of the entry

        Returns
        -------
        True if the entry id is within this download archive. False otherwise.
        """
        return any(entry_id in line for line in self._download_archive_lines)

    def remove_entry(self, entry_id: str) -> "DownloadArchive":
        """
        Parameters
        ----------
        entry_id
            Entry ID to remove if it exists in this download archive

        Returns
        -------
        self
        """
        self._download_archive_lines = [
            line for line in self._download_archive_lines if entry_id not in line
        ]
        return self


class DownloadMappings:
    _strptime_format = "%Y-%m-%d"

    def __init__(self):
        """
        Initializes an empty mapping
        """
        self._entry_mappings: Dict[str, DownloadMapping] = {}

    @classmethod
    def from_file(cls, json_file_path: str) -> "DownloadMappings":
        """
        Parameters
        ----------
        json_file_path
            Path to a json file that contains download mappings

        Returns
        -------
        Instantiated DownloadMappings class
        """
        with open(json_file_path, "r", encoding="utf8") as json_file:
            entry_mappings_json = json.load(json_file)

        for uid in entry_mappings_json.keys():
            entry_mappings_json[uid] = DownloadMapping.from_dict(
                mapping_dict=entry_mappings_json[uid]
            )

        download_mappings = DownloadMappings()
        download_mappings._entry_mappings = entry_mappings_json
        return download_mappings

    @property
    def entry_ids(self) -> List[str]:
        """
        Returns
        -------
        List of entry ids in the mapping
        """
        return list(self._entry_mappings.keys())

    @property
    def is_empty(self) -> bool:
        """
        Returns
        -------
        True if there are no entry mappings. False otherwise.
        """
        return len(self._entry_mappings) == 0

    def add_entry(self, entry: Entry, entry_file_path: str) -> "DownloadMappings":
        """
        Adds a file path for the entry. An entry can map to multiple file paths.

        Parameters
        ----------
        entry
            Entry that this file belongs to
        entry_file_path
            Relative path to the file that belongs to the entry

        Returns
        -------
        self
        """
        if entry.uid not in self.entry_ids:
            self._entry_mappings[entry.uid] = DownloadMapping.from_entry(entry=entry)

        self._entry_mappings[entry.uid].file_names.add(entry_file_path)
        return self

    def remove_entry(self, entry_id: str) -> "DownloadMappings":
        """
        Parameters
        ----------
        entry_id
            Id of the entry to remove

        Returns
        -------
        self
        """
        if entry_id in self.entry_ids:
            del self._entry_mappings[entry_id]
        return self

    def get_entries_out_of_range(self, date_range: DateRange) -> Dict[str, DownloadMapping]:
        """
        Parameters
        ----------
        date_range
            Range of dates that entries' upload dates must be within

        Returns
        -------
        Dict of entry_id: mapping if the upload date is not in the date range
        """
        out_of_range_entry_mappings = copy.deepcopy(self._entry_mappings)
        for uid in list(out_of_range_entry_mappings.keys()):
            upload_date = datetime.strptime(
                out_of_range_entry_mappings[uid].upload_date,
                self._strptime_format,
            ).date()

            if upload_date in date_range:
                del out_of_range_entry_mappings[uid]

        return out_of_range_entry_mappings

    def to_file(self, output_json_file: str) -> "DownloadMappings":
        """
        Parameters
        ----------
        output_json_file
            Output json file path to write the download mappings to

        Returns
        -------
        self
        """
        # Create json string first to ensure it is valid before writing anything to file
        json_str = json.dumps(
            obj={
                uid: mapping.dict
                for uid, mapping in sorted(
                    self._entry_mappings.items(),
                    key=lambda item: item[1].upload_date,
                    reverse=True,
                )
            },
            indent=2,
        )

        with open(output_json_file, "w", encoding="utf8") as file:
            file.write(json_str)

        return self

    def to_download_archive(self) -> DownloadArchive:
        """
        Returns
        -------
        A DownloadArchive created from the DownloadMappings' ids and extractors. YTDL will use this
        to avoid redownloading entries already downloaded.
        """
        lines: List[str] = []
        for entry_id, metadata in self._entry_mappings.items():
            lines.append(f"{metadata.extractor} {entry_id}")

        return DownloadArchive(download_archive_lines=lines)


class EnhancedDownloadArchive:
    """
    Maintains ytdl's download archive file as well as create an additional mapping file to map
    ytdl ids to multiple files. Used to delete 'stale' files that are out of range based on the
    file's entry's upload date.

    Should be used in this order:

    1. self.prepare_download_archive()
        Internally calls...

        a. self._load()
           Checks the output directory to see if an existing enhanced download archive file
           exists. If so, load it into the class. Otherwise, initialize an empty instance of one.
        b. self._copy_to_working_directory()
           If the download archive was loaded successfully, create a ytdl download archive in the
           working directory. This will let ytdl know which files are already downloaded.
    2. ( Perform the ytdlp download using a download archive with the same name )
        a. An existing archive should have been copied into the working directory for reuse
    3. self.mapping.add_entry(entry, file_path)
        a. Should be called for any file created for the given entry that gets moved to the output
           directory
    4. OPTIONAL: self.remove_stale_files()
        a. After all files have been moved over in the output directory, remove any stale files that
           exist in there.
    5. self.save_download_archive()
        a. Save the updated mapping file to the output directory.
    6. ( Delete the working directory )
    """

    def __init__(self, subscription_name: str, working_directory: str, output_directory: str):
        self.subscription_name = subscription_name
        self.working_directory = working_directory
        self.output_directory = output_directory

        self._download_archive: Optional[DownloadArchive] = None
        self._download_mapping: Optional[DownloadMappings] = None

        self._logger = Logger.get(name=subscription_name)

    @property
    def archive_file_name(self) -> str:
        """
        Returns
        -------
        The download archive's file name (no path)
        """
        return f".ytdl-subscribe-{self.subscription_name}-download-archive.txt"

    @property
    def _mapping_file_name(self) -> str:
        """
        Returns
        -------
        The download mapping's file name (no path)
        """
        return f".ytdl-subscribe-{self.subscription_name}-download-mapping.json"

    @property
    def _mapping_output_file_path(self):
        """
        Returns
        -------
        The download mapping's file path in the output directory.
        """
        return str(Path(self.output_directory) / self._mapping_file_name)

    @property
    def _archive_working_file_path(self) -> str:
        """
        Returns
        -------
        The download archive's file path in the working directory.
        """
        return str(Path(self.working_directory) / self.archive_file_name)

    @property
    def mapping(self) -> DownloadMappings:
        """
        Returns
        -------
        Loaded DownloadMappings

        Raises
        ------
        ValueError
            If the download mappings was not loaded
        """
        if self._download_mapping is None:
            raise ValueError("Tried to use download mapping before it was loaded")
        return self._download_mapping

    def _load(self) -> "EnhancedDownloadArchive":
        """
        Tries to load download mappings if they are present in the output directory.
        If they are not, initialize an empty mapping.

        Returns
        -------
        self
        """
        # If a mapping file exists in the output directory, load it up.
        if os.path.isfile(self._mapping_output_file_path):
            self._download_mapping = DownloadMappings.from_file(
                json_file_path=self._mapping_output_file_path
            )
        # Otherwise, init an empty download mappings object. Keep _download_archive as None to
        # indicate it was not loaded
        else:
            self._download_mapping = DownloadMappings()

        return self

    def _copy_to_working_directory(self) -> "EnhancedDownloadArchive":
        """
        If the mapping is not empty, create a download archive from it and save it into the
        working directory. This will tell YTDL to not redownload already downloaded entries.

        Returns
        -------
        self
        """
        # If the download mapping is empty, do nothing since the ytdl downloader will create a new
        # download archive file
        if self.mapping.is_empty:
            return self

        # Otherwise, create a ytdl download archive file in the working directory.
        self.mapping.to_download_archive().to_file(self._archive_working_file_path)

        return self

    def prepare_download_archive(self) -> "EnhancedDownloadArchive":
        """
        Helper function to load mappings and create a YTDL download archive file in the
        working directory if mappings exist.

        Returns
        -------
        self
        """
        self._load()
        self._copy_to_working_directory()
        return self

    def remove_stale_files(self, date_range: DateRange) -> "EnhancedDownloadArchive":
        """
        Checks all entries within the mappings. If any entries' upload dates are not within the
        provided date range, delete them.

        Parameters
        ----------
        date_range
            Date range the upload date must be in to not get deleted

        Returns
        -------
        self
        """
        stale_mappings: Dict[str, DownloadMapping] = self.mapping.get_entries_out_of_range(
            date_range=date_range
        )

        for uid, mapping in stale_mappings.items():
            self._logger.info("[%s] Removing the following stale file(s):", uid)
            for file_name in mapping.file_names:
                file_path = Path(self.output_directory) / Path(file_name)
                self._logger.info("  - %s", file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)

            self.mapping.remove_entry(entry_id=uid)

        return self

    def save_download_mappings(self) -> "EnhancedDownloadArchive":
        """
        Saves the updated download mappings to the output directory

        Returns
        -------
        self
        """
        # TODO: Make sure this logic is actually right...
        # Load the download archive from the working directory, which should contain any past
        # and new entries downloaded in this session
        self._download_archive = DownloadArchive.from_file(self._archive_working_file_path)

        # Keep the download archive in sync with the mapping
        for entry_id in self.mapping.entry_ids:
            if not self._download_archive.contains(entry_id):
                self._download_archive.remove_entry(entry_id)

        # Save the updated mapping file to the output directory
        self._download_mapping.to_file(output_json_file=self._mapping_output_file_path)

        return self
