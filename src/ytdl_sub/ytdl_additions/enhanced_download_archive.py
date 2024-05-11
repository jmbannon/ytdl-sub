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
from yt_dlp.utils import make_archive_id

from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.entry import ytdl_sub_split_by_chapters_parent_uid
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger

logger = Logger.get("archive")

v: VariableDefinitions = VARIABLES


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
            upload_date=entry.get(v.upload_date_standardized, str),
            extractor=entry.download_archive_extractor,
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
        # If no download archive file exists, instantiate an empty one
        if not os.path.isfile(file_path):
            return cls(download_archive_lines=[])

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
    def entry_mappings(self) -> Dict[str, DownloadMapping]:
        """
        Returns
        -------
        Mapping of entries to files
        """
        return self._entry_mappings

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
        return self.get_num_entries() == 0

    def add_entry(self, entry: Entry, entry_file_path: str) -> "DownloadMappings":
        """
        Adds a file path for the entry. An entry can map to multiple file paths.

        Parameters
        ----------
        entry
            Entry that this file belongs to
        entry_file_path
            Relative path to the file that lives in the output directory

        Returns
        -------
        self
        """
        uid = entry.uid
        if parent_uid := entry.try_get(ytdl_sub_split_by_chapters_parent_uid, str):
            uid = parent_uid

        if uid not in self.entry_ids:
            self._entry_mappings[uid] = DownloadMapping.from_entry(entry=entry)

        self._entry_mappings[uid].file_names.add(entry_file_path)
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

    def get_num_entries_with_upload_date(self, upload_date_standardized: str) -> int:
        """
        Parameters
        ----------
        upload_date_standardized
            A standardized upload date

        Returns
        -------
        Number of entries in the mapping with this upload date
        """
        return len(
            [_ for _ in self._entry_mappings.values() if _.upload_date == upload_date_standardized]
        )

    def get_num_entries(self) -> int:
        """
        Returns
        -------
        Number of entries in the mapping
        """
        return len(self._entry_mappings)

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
            sort_keys=True,
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
            lines.append(make_archive_id(ie=metadata.extractor, video_id=entry_id))

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
        b. self._move_to_working_directory()
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

    @classmethod
    def _maybe_load_download_mappings(
        cls, mapping_file_path: str, migrated_mapping_file_path: Optional[str]
    ) -> DownloadMappings:
        """
        Tries to load download mappings if a file exists. Otherwise returns empty mappings.
        """
        if migrated_mapping_file_path is not None:
            if os.path.isfile(migrated_mapping_file_path):
                logger.warning(
                    "MIGRATION SUCCESSFUL, loading migrated archive file. Can now set "
                    "`output_options.migrated_download_archive` to "
                    "`output_options.download_archive`"
                )
                return DownloadMappings.from_file(migrated_mapping_file_path)

            logger.warning(
                "MIGRATION DETECTED, will write archive file to %s", migrated_mapping_file_path
            )

        if os.path.isfile(mapping_file_path):
            return DownloadMappings.from_file(json_file_path=mapping_file_path)
        return DownloadMappings()

    def __init__(
        self,
        file_name: str,
        working_directory: str,
        output_directory: str,
        dry_run: bool = False,
        migrated_file_name: Optional[str] = None,
    ):
        self._file_name = file_name
        self._file_handler = FileHandler(
            working_directory=working_directory, output_directory=output_directory, dry_run=dry_run
        )
        self._download_mapping = DownloadMappings()  # gets reinitialized
        self._migrated_file_name = migrated_file_name

        self.num_entries_added: int = 0
        self.num_entries_modified: int = 0
        self.num_entries_removed: int = 0

    @property
    def num_entries(self) -> int:
        """
        Returns
        -------
        Total number of entries in the mapping
        """
        return self.mapping.get_num_entries()

    def reinitialize(self, dry_run: bool) -> "EnhancedDownloadArchive":
        """
        Re-initialize the enhanced download archive for successive downloads w/the same
        subscription.

        Parameters
        ----------
        dry_run
            Whether to actually move files to the output directory

        Returns
        -------
        self
        """
        self._file_handler = FileHandler(
            working_directory=self.working_directory,
            output_directory=self.output_directory,
            dry_run=dry_run,
        )
        self._download_mapping = self._maybe_load_download_mappings(
            mapping_file_path=self._output_file_path,
            migrated_mapping_file_path=self._migrated_file_path,
        )
        return self

    @property
    def is_dry_run(self) -> bool:
        """
        Returns
        -------
        True if this session is a dry-run. False otherwise.
        """
        return self._file_handler.dry_run

    @property
    def working_directory(self) -> str:
        """
        Returns
        -------
        Path to the working directory
        """
        return self._file_handler.working_directory

    @property
    def output_directory(self) -> str:
        """
        Returns
        -------
        Path to the output directory
        """
        return self._file_handler.output_directory

    @property
    def file_name(self) -> str:
        """
        Returns
        -------
        The download mapping's file name (no path)
        """
        return self._file_name

    @property
    def _output_file_path(self) -> str:
        """
        Returns
        -------
        The download mapping's file path in the output directory.
        """
        return str(Path(self.output_directory) / self.file_name)

    @property
    def _migrated_file_path(self) -> Optional[str]:
        """
        Returns
        -------
        The migrated download mapping's file path in the output directory.
        """
        if self._migrated_file_name:
            return str(Path(self.output_directory) / self._migrated_file_name)
        return None

    @property
    def working_file_path(self) -> str:
        """
        Returns
        -------
        The download mapping's file path in the working directory for ytdl usage
        """
        return str(Path(self.working_directory) / self.file_name)

    @property
    def working_ytdl_file_path(self) -> str:
        """
        Returns
        -------
        The download mapping's file path in the working directory for ytdl usage
        """
        return f"{self.working_file_path}-ytdl-archive"

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

    def prepare_download_archive(self) -> "EnhancedDownloadArchive":
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
        self.mapping.to_download_archive().to_file(self.working_ytdl_file_path)

        return self

    def _remove_entry(self, uid: str, mapping: DownloadMapping) -> None:
        for file_name in mapping.file_names:
            self._file_handler.delete_file_from_output_directory(file_name=file_name)

        self.mapping.remove_entry(entry_id=uid)
        self.num_entries_removed += 1

    def remove_stale_files(
        self, date_range: Optional[DateRange], keep_max_files: Optional[int]
    ) -> "EnhancedDownloadArchive":
        """
        Checks all entries within the mappings. If any entries' upload dates are not within the
        provided date range, delete them.

        Parameters
        ----------
        date_range
            Optional. Date range the upload date must be in to not get deleted
        keep_max_files
            Optional. Max number of files to keep

        Returns
        -------
        self
        """
        if date_range is not None:
            stale_mappings: Dict[str, DownloadMapping] = self.mapping.get_entries_out_of_range(
                date_range=date_range
            )

            for uid, mapping in stale_mappings.items():
                self._remove_entry(uid=uid, mapping=mapping)

        if keep_max_files is not None and keep_max_files > 0:
            num_files = 0
            for uid, mapping in sorted(
                self.mapping.entry_mappings.items(),
                key=lambda kv_: kv_[1].upload_date,
                reverse=True,
            ):
                num_files += 1
                if num_files > keep_max_files:
                    self._remove_entry(uid=uid, mapping=mapping)

        return self

    def save_download_mappings(self) -> "EnhancedDownloadArchive":
        """
        Saves the updated download mappings to the output directory if any files were changed.

        Returns
        -------
        self
        """
        # If a migrated file name is present, always save to that file
        if self._migrated_file_name:
            self._download_mapping.to_file(output_json_file=self.working_file_path)
            self.save_file_to_output_directory(
                file_name=self.file_name, output_file_name=self._migrated_file_name, copy_file=True
            )
            FileHandler.delete(file_path=self.working_file_path)

            # and delete the old one if the name differs
            if self._file_name != self._migrated_file_name:
                self.delete_file_from_output_directory(file_name=self.file_name)
        # Otherwise, only save if there are changes to the transaction log
        elif not self.get_file_handler_transaction_log().is_empty:
            self._download_mapping.to_file(output_json_file=self.working_file_path)
            self.save_file_to_output_directory(file_name=self.file_name, copy_file=True)
            FileHandler.delete(file_path=self.working_file_path)
        return self

    def delete_file_from_output_directory(self, file_name: str):
        """
        Deletes a file from the output directory

        Parameters
        ----------
        file_name
            Name of the file, relative to the output directory
        """
        return self._file_handler.delete_file_from_output_directory(file_name=file_name)

    def save_file_to_output_directory(
        self,
        file_name: str,
        file_metadata: Optional[FileMetadata] = None,
        output_file_name: Optional[str] = None,
        entry: Optional[Entry] = None,
        copy_file: bool = False,
    ):
        """
        Saves a file from the working directory to the output directory and record it in the
        transaction log.

        Parameters
        ----------
        file_name
            Name of the file to move (does not include working directory path)
        file_metadata
            Optional. Metadata to record to the transaction log for this file
        output_file_name
            Optional. Final name of the file in the output directory (does not include output
            directory path). If None, use the same working_directory file_name
        entry
            Optional. Entry that this file belongs to
        copy_file
            Optional. If True, copy the file. Move otherwise
        """
        if output_file_name is None:
            output_file_name = file_name

        if entry:
            self.mapping.add_entry(entry=entry, entry_file_path=output_file_name)

        is_modified = self._file_handler.move_file_to_output_directory(
            file_name=file_name,
            file_metadata=file_metadata,
            output_file_name=output_file_name,
            copy_file=copy_file,
        )

        # Determine if it's the entry file by seeing if the file_name to move matches the entry
        # download file name
        is_entry_file = entry and entry.get_download_file_name() == file_name
        if is_entry_file and is_modified:
            self.num_entries_modified += 1
        elif is_entry_file:
            self.num_entries_added += 1

    def get_file_handler_transaction_log(self) -> FileHandlerTransactionLog:
        """
        Returns
        -------
        File handler transaction log for this session
        """
        return self._file_handler.file_handler_transaction_log


class DownloadArchiver:
    """
    Used for any class that saves files. Does not allow direct access to output_directory,
    forcing the user of the class to use ``save_file`` so it gets archived and avoids any writes
    during dry-run.
    """

    def __init__(self, enhanced_download_archive: EnhancedDownloadArchive):
        self._enhanced_download_archive = enhanced_download_archive

    @property
    def working_directory(self) -> str:
        """
        Returns
        -------
        Path to the working directory
        """
        return self._enhanced_download_archive.working_directory

    @property
    def is_dry_run(self) -> bool:
        """
        Returns
        -------
        True if this session is a dry-run. False otherwise.
        """
        return self._enhanced_download_archive.is_dry_run

    def save_file(
        self,
        file_name: str,
        file_metadata: Optional[FileMetadata] = None,
        output_file_name: Optional[str] = None,
        entry: Optional[Entry] = None,
        copy_file: bool = False,
    ) -> None:
        """
        Saves a file in the working directory to the output directory.

        Parameters
        ----------
        file_name
            Name of the file relative to the working directory
        file_metadata
            Optional. Metadata to record to the transaction log for this file
        output_file_name
            Optional. Final name of the file in the output directory (does not include output
            directory path). If None, use the same working_directory file_name
        entry
            Optional. Entry that the file belongs to
        copy_file
            Optional. If True, copy the file. Move otherwise
        """
        self._enhanced_download_archive.save_file_to_output_directory(
            file_name=file_name,
            file_metadata=file_metadata,
            output_file_name=output_file_name,
            entry=entry,
            copy_file=copy_file,
        )
