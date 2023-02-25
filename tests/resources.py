import shutil
from pathlib import Path

REGENERATE_FIXTURES: bool = False

RESOURCE_PATH: Path = Path("tests") / "resources"
_FILE_FIXTURE_PATH: Path = RESOURCE_PATH / "file_fixtures"


def copy_file_fixture(fixture_name: str, output_file_path: Path) -> None:
    shutil.copy(_FILE_FIXTURE_PATH / fixture_name, output_file_path)
