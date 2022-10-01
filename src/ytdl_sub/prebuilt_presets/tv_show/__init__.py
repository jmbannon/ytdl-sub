from typing import Any
from typing import Dict
from typing import List
from typing import Optional

Preset = Dict[str, Any]


class PrebuiltPresets:
    BASE_PRESET: str

    def _preset(self, name: str, presets: List[str]) -> Preset:
        return {"presets": {name: {"preset": [self.BASE_PRESET] + presets}}}

    def _tv_show_url(self, name: str) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._preset(
            name=name, presets=["tv_show_url", "season_by_year__episode_by_month_day"]
        )

    def _tv_show_collection(self, name: str) -> Preset:
        return self._preset(
            name=name,
            presets=["tv_show_collection", "season_by_collection__episode_by_year_month_day"],
        )

    @classmethod
    def get_preset_names(cls) -> List[str]:
        preset_names = [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property)]
        return preset_names

    @classmethod
    def get_collection_preset_names(cls) -> List[str]:
        return [name for name in cls.get_preset_names() if "collection" in name]

    @classmethod
    def get_non_collection_preset_names(cls) -> List[str]:
        return [name for name in cls.get_preset_names() if "collection" not in name]

    @classmethod
    def get_presets(cls, preset_names: Optional[List[str]] = None) -> List[Preset]:
        if preset_names is None:
            preset_names = cls.get_preset_names()

        return [getattr(cls(), preset_name) for preset_name in preset_names]


class PrebuiltKodiTVShowPresets(PrebuiltPresets):
    BASE_PRESET = "kodi_tv_show"

    @property
    def kodi_tv_show_url(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._tv_show_url(name="kodi_tv_show_url")

    @property
    def kodi_tv_show_collection(self) -> Preset:
        """
        Kodi TV Show from a collection of multiple URLs. TODO: finish docstring
        """
        return self._tv_show_collection(name="kodi_tv_show_collection")


class PrebuiltJellyfinTVShowPresets(PrebuiltPresets):
    BASE_PRESET = "jellyfin_tv_show"

    @property
    def jellyfin_tv_show_url(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._tv_show_url(name="jellyfin_tv_show_url")

    @property
    def jellyfin_tv_show_collection(self) -> Preset:
        """
        Kodi TV Show from a collection of multiple URLs. TODO: finish docstring
        """
        return self._tv_show_collection(name="jellyfin_tv_show_collection")


class PrebuiltPlexTVShowPresets(PrebuiltPresets):
    BASE_PRESET = "plex_tv_show"

    @property
    def plex_tv_show_url(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._tv_show_url(name="plex_tv_show_url")

    @property
    def plex_tv_show_collection(self) -> Preset:
        """
        Kodi TV Show from a collection of multiple URLs. TODO: finish docstring
        """
        return self._tv_show_collection(name="plex_tv_show_collection")
