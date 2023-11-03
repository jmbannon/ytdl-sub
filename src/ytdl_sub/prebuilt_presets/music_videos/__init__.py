from ytdl_sub.prebuilt_presets import PrebuiltPresets
from ytdl_sub.prebuilt_presets import get_prebuilt_preset_package_name

PREBUILT_PRESET_PACKAGE_NAME = get_prebuilt_preset_package_name(__file__)


class MusicVideoPresets(PrebuiltPresets):
    preset_names = {
        "Kodi Music Videos",
        "Jellyfin Music Videos",
        "Plex Music Videos",
    }
