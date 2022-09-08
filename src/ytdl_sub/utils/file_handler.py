import hashlib
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


def get_file_md5_hash(full_file_path: Path | str) -> str:
    """
    Parameters
    ----------
    full_file_path
        Path to the file

    Returns
    -------
    md5 hash of its contents
    """
    with open(full_file_path, "rb") as file:
        return hashlib.md5(file.read()).hexdigest()


def files_equal(full_file_path_a: Path | str, full_file_path_b: Path | str) -> bool:
    """
    Parameters
    ----------
    full_file_path_a
    full_file_path_b

    Returns
    -------
    True if the files are equal in contents. False otherwise.
    """
    if not (os.path.isfile(full_file_path_a) and os.path.isfile(full_file_path_b)):
        return False
    if os.path.getsize(full_file_path_a) != os.path.getsize(full_file_path_b):
        return False
    if get_file_md5_hash(full_file_path_a) != get_file_md5_hash(full_file_path_b):
        return False
    return True


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
            value_dict = json.loads(json.dumps(value_dict, sort_keys=True, ensure_ascii=False))

        def _indent_lines(value: str, indent: int) -> str:
            if "\n" not in value:
                return value

            output_str = ""
            _indent = " " * indent
            for line in value.split("\n"):
                output_str += f"{_indent}{line}\n"
            return f"{output_str.rstrip()}\n"

        def _single_value(value: Any) -> Optional[str]:
            if isinstance(value, list) and len(value) == 1:
                return _single_value(value=value[0])
            if isinstance(value, (dict, list)):
                return None
            if isinstance(value, str) and "\n" in value:
                return None
            return value

        def _recursive_lines(value: Any, indent: int = 0) -> str:
            _indent = " " * indent

            output_str = ""
            if isinstance(value, dict):
                for key, sub_value in value.items():
                    single_sub_value = _single_value(sub_value)
                    if single_sub_value is not None:
                        output_str += f"{_indent}{key}: {single_sub_value}\n"
                    else:
                        output_str += f"{_indent}{key}:\n"
                        output_str += _indent_lines(_recursive_lines(sub_value), indent=indent + 2)

            elif isinstance(value, list):
                for sub_value in value:
                    single_sub_value = _single_value(sub_value)
                    if single_sub_value is not None:
                        output_str += f"{_indent}- {single_sub_value}\n"
                    else:
                        output_str += f"{_indent}- \n"
                        output_str += _indent_lines(_recursive_lines(sub_value), indent=indent + 2)
            elif isinstance(value, str):  # multi-line string
                output_str += _indent_lines(value, indent=indent)
            else:
                assert False, "should never reach here"
            return output_str

        out = _recursive_lines(value_dict).rstrip().split("\n")
        return cls(metadata=out)


class FileHandlerTransactionLog:
    """
    Tracks file 'transactions' performed by a FileHandler
    """

    def __init__(self):
        self.files_created: Dict[str, FileMetadata] = {}
        self.files_modified: Dict[str, FileMetadata] = {}
        self.files_removed: Set[str] = set()

    @property
    def is_empty(self) -> bool:
        """
        Returns
        -------
        True if no transaction logs are recorded. False otherwise
        """
        return (
            len(self.files_created) == 0
            and len(self.files_removed) == 0
            and len(self.files_modified) == 0
        )

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

    def log_modified_file(
        self, file_name: str, file_metadata: Optional[FileMetadata] = None
    ) -> "FileHandlerTransactionLog":
        """
        Adds a modified file to the transaction log

        Parameters
        ----------
        file_name
            Name of the file in the output directory
        file_metadata
            Optional. If the file has metadata, add it to the transaction log
        """
        if not file_metadata:
            file_metadata = FileMetadata()

        self.files_modified[file_name] = file_metadata
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

        line_dash = "-" * 40

        if self.files_created:
            created_line = f"Files created in '{output_directory}'"
            lines.extend([created_line, line_dash])
            for file_path, file_metadata in sorted(self.files_created.items()):
                lines.append(file_path)
                if file_metadata:
                    lines.extend([_indent_metadata_line(line) for line in file_metadata.metadata])

        if self.files_modified:
            modified_line = f"Files modified in '{output_directory}'"
            lines.extend([modified_line, line_dash])
            for file_path, file_metadata in sorted(self.files_modified.items()):
                lines.append(file_path)
                if file_metadata:
                    lines.extend([_indent_metadata_line(line) for line in file_metadata.metadata])

        if self.files_removed:
            # Add a blank line to separate created/removed files
            if self.files_created:
                lines.append("")

            removed_line = f"Files removed from '{output_directory}'"
            lines.extend([removed_line, line_dash])
            for file_path in sorted(self.files_removed):
                lines.append(file_path)

        if self.is_empty:
            lines.append(f"No new, modified, or removed files in '{output_directory}'")

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
        source_file_path = Path(self.working_directory) / file_name
        output_file_path = Path(self.output_directory) / output_file_name

        # output file exists, see if we modify it
        if os.path.isfile(output_file_path):
            if not files_equal(source_file_path, output_file_path):
                self._file_handler_transaction_log.log_modified_file(
                    file_name=output_file_name, file_metadata=file_metadata
                )
        # output file does not already exist, creates a new file
        else:
            self._file_handler_transaction_log.log_created_file(
                file_name=output_file_name, file_metadata=file_metadata
            )

        if not self.dry_run:
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            self.move(src_file_path=source_file_path, dst_file_path=output_file_path)

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
