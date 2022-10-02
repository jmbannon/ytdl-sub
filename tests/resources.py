import shutil
from pathlib import Path

RESOURCE_PATH = Path("tests/resources")
_FILE_FIXTURE_PATH = RESOURCE_PATH / "file_fixtures"


def copy_file_fixture(fixture_name: str, output_file_path: str | Path) -> None:
    shutil.copy(_FILE_FIXTURE_PATH / fixture_name, output_file_path)
