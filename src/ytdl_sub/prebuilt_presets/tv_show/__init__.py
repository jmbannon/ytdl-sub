from ytdl_sub.prebuilt_presets import PrebuiltPresets
from ytdl_sub.prebuilt_presets import get_prebuilt_preset_package_name

PREBUILT_PRESET_PACKAGE_NAME = get_prebuilt_preset_package_name(__file__)


class TvShowByDatePresets(PrebuiltPresets):
    preset_names = {
        "Kodi TV Show by Date",
        "Jellyfin TV Show by Date",
        "Emby TV Show by Date",
        "Plex TV Show by Date",
    }


class TvShowCollectionPresets(PrebuiltPresets):
    preset_names = {
        "Kodi TV Show Collection",
        "Jellyfin TV Show Collection",
        "Emby TV Show Collection",
        "Plex TV Show Collection",
    }
