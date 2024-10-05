import os
import shutil
from pathlib import Path

REGENERATE_FIXTURES: bool = True

RESOURCE_PATH: Path = Path("tests") / "resources"
_FILE_FIXTURE_PATH: Path = RESOURCE_PATH / "file_fixtures"


def file_fixture_path(fixture_name: str) -> Path:
    return _FILE_FIXTURE_PATH / fixture_name


def copy_file_fixture(fixture_name: str, output_file_path: Path) -> None:
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    shutil.copy(file_fixture_path(fixture_name), output_file_path)
