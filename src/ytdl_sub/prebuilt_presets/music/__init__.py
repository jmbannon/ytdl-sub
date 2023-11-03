from ytdl_sub.prebuilt_presets import PrebuiltPresets
from ytdl_sub.prebuilt_presets import get_prebuilt_preset_package_name

PREBUILT_PRESET_PACKAGE_NAME = get_prebuilt_preset_package_name(__file__)


class MusicPresets(PrebuiltPresets):
    preset_names = {
        "Single",
        "SoundCloud Discography",
        "YouTube Releases",
        "YouTube Full Albums",
        "Bandcamp",
    }
