import hashlib
import json
import os
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

from ytdl_sub.utils.subtitles import SUBTITLE_EXTENSIONS


def get_file_extension(file_name: Path | str) -> str:
    """
    Returns the file extension from a file name. Tries to return .info.json and .lang.subtitle
    extensions if detected, otherwise splits on the last `.` and returns the latter part
    """
    if file_name.endswith(".info.json"):
        return "info.json"
    if any(file_name.endswith(f".{subtitle_ext}") for subtitle_ext in SUBTITLE_EXTENSIONS):
        file_name_split = file_name.split(".")
        ext = file_name_split[-1]

        # Try to capture .lang.ext
        if len(file_name_split) > 2 and len(file_name_split[-2]) < 6:
            ext = f"{file_name_split[-2]}.{file_name_split[-1]}"

        return ext
    return file_name.rsplit(".", maxsplit=1)[-1]


def get_md5_hash(contents: str) -> str:
    """
    Helper function to compute md5 hash
    """
    return hashlib.md5(contents.encode()).hexdigest()


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
    md5hash = hashlib.md5()
    block_size = 128 * 1000  # md5 uses 128-byte digest blocks
    with open(full_file_path, "rb") as file:
        while chunk := file.read(block_size):
            md5hash.update(chunk)
    return md5hash.hexdigest()


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

    @classmethod
    def format_path_str(cls, path_str: Path | str) -> str:
        """
        Returns
        -------
        str formatted to always look like a unix string
        """
        return str(path_str).replace(os.sep, "/")

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

    @classmethod
    def _indent_metadata_line(cls, line: str, indent: int) -> str:
        # Do not indent empty lines
        rstrip_line = line.rstrip()
        indent_str = " " * indent
        return f"{indent_str}{rstrip_line}" if rstrip_line else ""

    @classmethod
    def _to_output_message(
        cls, file_set_title: str, file_set: Dict[str, Optional[FileMetadata]], output_directory: str
    ) -> List[str]:
        if not file_set:
            return []

        directory_set: Dict[str, Dict[str, Optional[FileMetadata]]] = defaultdict(dict)
        for file_path, file_metadata in sorted(file_set.items()):
            file_directory = os.path.dirname(Path(output_directory) / file_path)
            file_name = os.path.basename(Path(output_directory) / file_path)

            # Format file directories/names to always look like unix
            file_directory = cls.format_path_str(file_directory)
            file_name = cls.format_path_str(file_name)

            directory_set[file_directory][file_name] = file_metadata

        lines: List[str] = [file_set_title, "-" * 40]
        for directory, directory_file_set in directory_set.items():
            lines.append(directory)
            for file_name, file_metadata in directory_file_set.items():
                lines.append(cls._indent_metadata_line(file_name, indent=2))

                if not file_metadata:
                    continue

                lines.extend(
                    [cls._indent_metadata_line(line, indent=4) for line in file_metadata.metadata]
                )

        return lines

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

        if self.files_created:
            lines.extend(
                self._to_output_message(
                    file_set_title="Files created:",
                    file_set=self.files_created,
                    output_directory=output_directory,
                )
            )

        if self.files_modified:
            # Add a blank line to separate created files
            if self.files_created:
                lines.append("")

            lines.extend(
                self._to_output_message(
                    file_set_title="Files modified:",
                    file_set=self.files_modified,
                    output_directory=output_directory,
                )
            )

        if self.files_removed:
            # Add a blank line to separate created/removed files
            if self.files_created or self.files_modified:
                lines.append("")

            lines.extend(
                self._to_output_message(
                    file_set_title="Files removed:",
                    file_set={file_name: None for file_name in self.files_removed},
                    output_directory=output_directory,
                )
            )

        if self.is_empty:
            lines.append(
                f"No new, modified, or removed files in '{self.format_path_str(output_directory)}'"
            )

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
        # Perform the copy by first writing to a temp file, then moving it.
        # This tries to prevent corrupted writes if the processed dies mid-write,
        atomic_dst = f"{dst_file_path}-ytdl-sub-incomplete"
        shutil.copyfile(src=src_file_path, dst=atomic_dst)
        shutil.move(src=atomic_dst, dst=dst_file_path)

    @classmethod
    def move(cls, src_file_path: Union[str, Path], dst_file_path: Union[str, Path]):
        """
        Parameters
        ----------
        src_file_path
            Source file
        dst_file_path
            Destination file

        Raises
        ------
        OSError
            Cross-device link workaround
        """
        try:
            shutil.move(src=src_file_path, dst=dst_file_path)
        except OSError:
            # Invalid cross-device link
            # Can happen from using os.rename under the hood, which requires the two file on the
            # same filesystem. Work around it by copying and deleting the file
            cls.copy(src_file_path, dst_file_path)
            cls.delete(src_file_path)

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
        self,
        file_name: str,
        output_file_name: str,
        file_metadata: Optional[FileMetadata] = None,
        copy_file: bool = False,
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
        copy_file
            Optional. If True, copy the file. Move otherwise

        Returns
        -------
        bool
            True if modified. False otherwise.
        """
        is_modified = False
        source_file_path = Path(self.working_directory) / file_name
        output_file_path = Path(self.output_directory) / output_file_name

        # output file exists, and it's not marked as created already, see if we modify it
        if (
            os.path.isfile(output_file_path)
            and output_file_name not in self.file_handler_transaction_log.files_created
        ):
            if not files_equal(source_file_path, output_file_path):
                self.file_handler_transaction_log.log_modified_file(
                    file_name=output_file_name, file_metadata=file_metadata
                )
                is_modified = True
        # output file does not already exist, creates a new file
        else:
            self.file_handler_transaction_log.log_created_file(
                file_name=output_file_name, file_metadata=file_metadata
            )

        if not self.dry_run:
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            if copy_file:
                self.copy(src_file_path=source_file_path, dst_file_path=output_file_path)
            else:
                self.move(src_file_path=source_file_path, dst_file_path=output_file_path)
        # Simulate the file being moved during dry run by deleting it
        elif self.dry_run and not copy_file:
            FileHandler.delete(source_file_path)

        return is_modified

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
