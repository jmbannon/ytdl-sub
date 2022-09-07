import json
import os
import shutil
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union
import yaml


class FileMetadata:
    """
    Stores pretty-printed information about a file. Each line in the metadata represents a newline
    """

    def __init__(self, metadata: Optional[Union[str, List[str]]] = None):
        self.metadata = []
        if isinstance(metadata, str):
            self.metadata = [metadata]
        elif isinstance(metadata, list):
            self.metadata = metadata

    def append(self, line: str) -> "FileMetadata":
        """
        Parameters
        ----------
        line
            Line of metadata to append
        """
        self.metadata.append(line)
        return self

    def extend(self, other: Optional["FileMetadata"]) -> "FileMetadata":
        """
        Parameters
        ----------
        other
            Other metadata to extend to this one in its entirety
        """
        if other is not None:
            self.metadata.extend(other.metadata)
        return self

    @classmethod
    def from_dict(
        cls, value_dict: Dict[str, Any], title: Optional[str] = None, sort_dict: bool = True
    ) -> "FileMetadata":
        """
        Parameters
        ----------
        value_dict
            Dict of things to print indented
        title
            Optional. Title line to put above the dict
        sort_dict
            Whether to sort dicts in the value_dict. Defaults to true.
        """
        if title:
            value_dict = {title: value_dict}
        if sort_dict:
            value_dict = json.loads(json.dumps(value_dict, sort_keys=True))

        out = yaml.safe_dump(value_dict, allow_unicode=True, indent=2, default_style='', width=100)
        return cls(metadata=out.rstrip().split('\n'))


class FileHandlerTransactionLog:
    """
    Tracks file 'transactions' performed by a FileHandler
    """

    def __init__(self):
        self.files_created: Dict[str, FileMetadata] = {}
        self.files_removed: Set[str] = set()

    @property
    def is_empty(self) -> bool:
        """
        Returns
        -------
        True if no transaction logs are recorded. False otherwise
        """
        return len(self.files_created) == 0 and len(self.files_removed) == 0

    def log_created_file(
        self, file_name: str, file_metadata: Optional[FileMetadata] = None
    ) -> "FileHandlerTransactionLog":
        """
        Adds a created file to the transaction log

        Parameters
        ----------
        file_name
            Name of the file in the output directory
        file_metadata
            Optional. If the file has metadata, add it to the transaction log
        """
        if not file_metadata:
            file_metadata = FileMetadata()

        self.files_created[file_name] = file_metadata
        return self

    def log_removed_file(self, file_name: str) -> "FileHandlerTransactionLog":
        """
        Records a file removed from the output directory
        Parameters
        ----------
        file_name
            Name of the file in the output directory getting removed
        """
        self.files_removed.add(file_name)
        return self

    def to_output_message(self, output_directory: str) -> str:
        """
        Parameters
        ----------
        output_directory
            Path to the output directory. Included in the output message

        Returns
        -------
        The output message to show users what was recorded in the transaction log
        """
        lines: List[str] = []

        def _indent_metadata_line(line: str) -> str:
            # Do not indent empty lines
            rstrip_line = line.rstrip()
            return f"  {rstrip_line}" if rstrip_line else ""

        if self.files_created:
            created_line = f"Files created in '{output_directory}'"
            created_line_dash = "-" * 40
            lines.extend([created_line, created_line_dash])
            for file_path, file_metadata in sorted(self.files_created.items()):
                lines.append(file_path)
                if file_metadata:
                    lines.extend([_indent_metadata_line(line) for line in file_metadata.metadata])

        if self.files_removed:
            # Add a blank line to separate created/removed files
            if self.files_created:
                lines.append("")

            removed_line = f"Files removed from '{output_directory}'"
            removed_line_dash = "-" * 40
            lines.extend([removed_line, removed_line_dash])
            for file_path in sorted(self.files_removed):
                lines.append(file_path)

        return "\n".join(lines)


class FileHandler:
    """
    Performs and tracks all file moving/copying/deleting
    """

    def __init__(self, working_directory: str, output_directory: str, dry_run: bool):
        self.dry_run = dry_run
        self.working_directory = working_directory
        self.output_directory = output_directory
        self._file_handler_transaction_log = FileHandlerTransactionLog()

    @property
    def file_handler_transaction_log(self) -> FileHandlerTransactionLog:
        """
        Returns
        -------
        Transaction logs of this file handler
        """
        return self._file_handler_transaction_log

    @classmethod
    def copy(cls, src_file_path: Union[str, Path], dst_file_path: Union[str, Path]):
        """
        Parameters
        ----------
        src_file_path
            Source file
        dst_file_path
            Destination file
        """
        shutil.copyfile(src=src_file_path, dst=dst_file_path)

    @classmethod
    def move(cls, src_file_path: Union[str, Path], dst_file_path: Union[str, Path]):
        """
        Parameters
        ----------
        src_file_path
            Source file
        dst_file_path
            Destination file
        """
        shutil.move(src=src_file_path, dst=dst_file_path)

    @classmethod
    def delete(cls, file_path: Union[str, Path]):
        """
        Parameters
        ----------
        file_path
            File to delete
        """
        if os.path.isfile(file_path):
            os.remove(file_path)

    def move_file_to_output_directory(
        self, file_name: str, output_file_name: str, file_metadata: Optional[FileMetadata] = None
    ):
        """
        Copies a file from the working directory to the output directory.
        All file copies from working to output directory should use this function for tracking and
        handling dry-run logic.

        Parameters
        ----------
        file_name
            File in the working directory
        output_file_name
            Desired output file name in the output_directory
        file_metadata
            Optional. Metadata to record to the transaction log for this file
        """
        self._file_handler_transaction_log.log_created_file(
            file_name=output_file_name, file_metadata=file_metadata
        )

        if not self.dry_run:
            output_file_path = Path(self.output_directory) / output_file_name
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            self.move(
                src_file_path=Path(self.working_directory) / file_name,
                dst_file_path=output_file_path,
            )

    def delete_file_from_output_directory(self, file_name: str):
        """
        Deletes a file from the output directory. All file deletions should use this function
        for tracking and handling dry-run logic.

        Parameters
        ----------
        file_name
            File in the output directory to delete
        """
        file_path = Path(self.output_directory) / file_name
        exists = os.path.isfile(file_path)

        if exists:
            self._file_handler_transaction_log.log_removed_file(file_name)
            if not self.dry_run:
                self.delete(file_path=file_path)
