import os
import pathlib
from typing import Any
from typing import Dict
from typing import Set

import mergedeep

from ytdl_sub.utils.yaml import load_yaml


def get_prebuilt_preset_package_name(path: pathlib.Path) -> str:
    """
    Returns
    -------
    Package name for prebuilt presets
    """
    return os.path.basename(os.path.dirname(path))


def _merge_presets() -> Dict[str, Any]:
    merged_configs: Dict[str, Any] = {}

    # Get all presets from the loose YAML files
    for file in pathlib.Path(__file__).parent.resolve().rglob("*"):
        if file.is_file() and file.name.endswith("yaml"):
            mergedeep.merge(merged_configs, load_yaml(file))

    return merged_configs["presets"]


PREBUILT_PRESETS: Dict[str, Any] = _merge_presets()

PREBUILT_PRESET_NAMES: Set[str] = set(PREBUILT_PRESETS.keys())
PUBLISHED_PRESET_NAMES: Set[str] = {
    name for name in PREBUILT_PRESET_NAMES if not name.startswith("_")
}


class PrebuiltPresets:
    preset_names: Set[str]
