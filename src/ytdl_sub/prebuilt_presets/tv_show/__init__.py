from typing import Any
from typing import Dict
from typing import List
from typing import Optional

Preset = Dict[str, Any]

KODI_TV_SHOW = "kodi_tv_show"
JELLYFIN_TV_SHOW = "jellyfin_tv_show"
PLEX_TV_SHOW = "plex_tv_show"

TV_SHOW_URL = "tv_show_url"
TV_SHOW_COLLECTION = "tv_show_collection"


class PrebuiltPresets:
    @classmethod
    def _build_preset(cls, name: str, parent_presets: List[str]) -> Preset:
        return {"presets": {name: {"preset": parent_presets}}}

    @classmethod
    def get_preset_names(cls) -> List[str]:
        preset_names = [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property)]
        return preset_names

    @classmethod
    def get_presets(cls) -> List[Preset]:
        return [getattr(cls(), preset_name) for preset_name in cls.get_preset_names()]


class PrebuiltTvShowUrlPresets(PrebuiltPresets):
    """
    Docstring for all TV SHOW URL presets
    """

    BASE_PRESET = "tv_show_url"

    @property
    def kodi_tv_show_url(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._build_preset(
            name="kodi_tv_show_url", parent_presets=[KODI_TV_SHOW, TV_SHOW_URL]
        )

    @property
    def jellyfin_tv_show_url(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._build_preset(
            name="jellyfin_tv_show_url", parent_presets=[JELLYFIN_TV_SHOW, TV_SHOW_URL]
        )

    @property
    def plex_tv_show_url(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._build_preset(
            name="plex_tv_show_url", parent_presets=[PLEX_TV_SHOW, TV_SHOW_URL]
        )


class PrebuiltTvShowCollectionPresets(PrebuiltPresets):
    """
    Docstring for all TV SHOW URL presets
    """

    @property
    def kodi_tv_show_collection(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._build_preset(
            name="kodi_tv_show_collection", parent_presets=[KODI_TV_SHOW, TV_SHOW_COLLECTION]
        )

    @property
    def jellyfin_tv_show_collection(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._build_preset(
            name="jellyfin_tv_show_collection",
            parent_presets=[JELLYFIN_TV_SHOW, TV_SHOW_COLLECTION],
        )

    @property
    def plex_tv_show_collection(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._build_preset(
            name="plex_tv_show_collection", parent_presets=[PLEX_TV_SHOW, TV_SHOW_COLLECTION]
        )
