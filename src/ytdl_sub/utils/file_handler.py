import os
from pathlib import Path
from shutil import copyfile
from typing import Set
from typing import Union


class FileHandler:
    """
    Performs and tracks all file moving/copying/deleting
    """

    def __init__(self, working_directory: str, output_directory: str, dry_run: bool):
        self.dry_run = dry_run
        self.working_directory = working_directory
        self.output_directory = output_directory

        self.files_created: Set[str] = set()
        self.files_deleted: Set[str] = set()

    @classmethod
    def copy(cls, src_file_path: Union[str, Path], dst_file_path: Union[str, Path]):
        copyfile(src=src_file_path, dst=dst_file_path)

    @classmethod
    def delete(cls, file_path: Union[str, Path]):
        if os.path.isfile(file_path):
            os.remove(file_path)

    def copy_file_to_output_directory(self, file_name: str, output_file_name: str):
        self.files_created.add(output_file_name)

        if not self.dry_run:
            output_file_path = Path(self.output_directory) / output_file_name
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            self.copy(
                src_file_path=Path(self.working_directory) / file_name,
                dst_file_path=output_file_path,
            )

    def delete_file_from_output_directory(self, file_name: str):
        file_path = Path(self.output_directory) / file_name
        exists = os.path.isfile(file_path)

        if exists:
            self.files_deleted.add(file_name)
            if not self.dry_run:
                self.delete(file_path=file_path)
