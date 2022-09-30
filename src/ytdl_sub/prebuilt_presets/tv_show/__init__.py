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
            name=name, presets=["tv-show-url", "season-by-year--episode-by-month-day"]
        )

    def _tv_show_youtube_channel(self, name: str) -> Preset:
        return self._preset(
            name=name, presets=["tv-show-youtube-channel", "season-by-year--episode-by-month-day"]
        )

    def _tv_show_collection(self, name: str) -> Preset:
        return self._preset(
            name=name,
            presets=["tv-show-collection", "season-by-collection--episode-by-year-month-day"],
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
    BASE_PRESET = "kodi-tv-show"

    @property
    def kodi_tv_show_url(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._tv_show_url(name="kodi_tv_show_url")

    @property
    def kodi_tv_show_youtube_channel(self) -> Preset:
        """
        Kodi TV Show from a YouTube channel with seasons as years, episodes ordered by upload date
        """
        return self._tv_show_youtube_channel(name="kodi_tv_show_youtube_channel")

    @property
    def kodi_tv_show_collection(self) -> Preset:
        """
        Kodi TV Show from a collection of multiple URLs. TODO: finish docstring
        """
        return self._tv_show_collection(name="kodi_tv_show_collection")


class PrebuiltJellyfinTVShowPresets(PrebuiltPresets):
    BASE_PRESET = "jellyfin-tv-show"

    @property
    def jellyfin_tv_show_url(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._tv_show_url(name="jellyfin_tv_show_url")

    @property
    def jellyfin_tv_show_youtube_channel(self) -> Preset:
        """
        Kodi TV Show from a YouTube channel with seasons as years, episodes ordered by upload date
        """
        return self._tv_show_youtube_channel(name="jellyfin_tv_show_youtube_channel")

    @property
    def jellyfin_tv_show_collection(self) -> Preset:
        """
        Kodi TV Show from a collection of multiple URLs. TODO: finish docstring
        """
        return self._tv_show_collection(name="jellyfin_tv_show_collection")
