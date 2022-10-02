import pathlib
from typing import Any
from typing import Dict

import mergedeep

from ytdl_sub.prebuilt_presets.tv_show import PrebuiltTvShowCollectionPresets
from ytdl_sub.prebuilt_presets.tv_show import TvShowByDatePresets
from ytdl_sub.utils.yaml import load_yaml


def _merge_presets() -> Dict[str, Any]:
    merged_configs: Dict[str, Any] = {}

    # Get all presets from the loose YAML files
    for file in pathlib.Path(__file__).parent.resolve().rglob("*"):
        if file.is_file() and file.name.endswith("yaml"):
            mergedeep.merge(merged_configs, load_yaml(file))

    # Get all presets from published preset configs
    mergedeep.merge(
        merged_configs,
        *TvShowByDatePresets.get_presets(),
        *PrebuiltTvShowCollectionPresets.get_presets(),
    )

    return merged_configs["presets"]


PREBUILT_PRESETS: Dict[str, Any] = _merge_presets()
