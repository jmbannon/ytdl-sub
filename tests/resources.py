import json
import os
import shutil
from pathlib import Path
from typing import Dict

DISABLE_YOUTUBE_TESTS: bool = True
REGENERATE_FIXTURES: bool = False

RESOURCE_PATH: Path = Path("tests") / "resources"
_FILE_FIXTURE_PATH: Path = RESOURCE_PATH / "file_fixtures"
_EXPECTED_JSON_PATH: Path = RESOURCE_PATH / "expected_json"


def file_fixture_path(fixture_name: str) -> Path:
    return _FILE_FIXTURE_PATH / fixture_name


def expected_json(input_json: Dict, json_name: str) -> Dict:
    if REGENERATE_FIXTURES:
        with open(_EXPECTED_JSON_PATH / json_name, "w", encoding="utf-8") as json_file:
            json.dump(input_json, json_file, sort_keys=True, indent=2)

        return input_json

    with open(_EXPECTED_JSON_PATH / json_name, "r", encoding="utf-8") as json_file:
        expected_json = json.load(json_file)

    return expected_json


def copy_file_fixture(fixture_name: str, output_file_path: Path) -> None:
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    shutil.copy(file_fixture_path(fixture_name), output_file_path)
