from typing import Any, Dict
from typing import List

Preset = Dict[str, Any]


class PrebuiltPresets:
    BASE_PRESET: str

    def _preset(self, name: str, presets: List[str]) -> Preset:
        return {
            "presets": {
                name: {
                    "preset": [self.BASE_PRESET] + presets
                }
            }
        }

    def _tv_show_url(self, name: str) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._preset(name=name, presets=["tv-show-url", "episode-by-month-day"])

    def _tv_show_url_reversed(self, name: str) -> Preset:
        return self._preset(name=name, presets=["tv-show-url", "episode-by-month-day-reversed"])

    def _tv_show_youtube_channel(self, name: str) -> Preset:
        return self._preset(name=name, presets=["tv-show-youtube-channel", "episode-by-month-day"])

    def _tv_show_youtube_channel_reversed(self, name: str) -> Preset:
        return self._preset(name=name, presets=["tv-show-youtube-channel", "episode-by-month-day"])

    def _tv_show_collection(self, name: str) -> Preset:
        return self._preset(name=name, presets=["tv-show-collection", "episode-by-year-month-day"])

    def _tv_show_collection_reversed(self, name: str) -> Preset:
        return self._preset(
            name=name, presets=["tv-show-collection", "episode-by-year-month-day-reversed"]
        )

    @classmethod
    def get_preset_names(cls) -> List[str]:
        preset_names = [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property)]
        return preset_names

    @classmethod
    def get_presets(cls) -> List[Preset]:
        return [getattr(cls(), preset_name) for preset_name in cls.get_preset_names()]


class PrebuiltKodiTVShowPresets(PrebuiltPresets):
    BASE_PRESET = "kodi-tv-show"

    @property
    def kodi_tv_show_url(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date
        """
        return self._tv_show_url(name="kodi_tv_show_url")

    @property
    def kodi_tv_show_url_reversed(self) -> Preset:
        """
        Kodi TV Show with seasons as years, episodes ordered by upload date in descending order
        (more recent uploads have smaller episode number)
        """
        return self._tv_show_url_reversed(name="kodi_tv_show_url_reversed")

    @property
    def kodi_tv_show_youtube_channel(self) -> Preset:
        """
        Kodi TV Show from a YouTube channel with seasons as years, episodes ordered by upload date
        """
        return self._tv_show_youtube_channel(name="kodi_tv_show_youtube_channel")

    @property
    def kodi_tv_show_youtube_channel_reversed(self) -> Preset:
        """
        Kodi TV Show from a YouTube channel with seasons as years, episodes ordered by upload date
        in descending order (more recent uploads have smaller episode number)
        """
        return self._tv_show_youtube_channel_reversed(name="kodi_tv_show_youtube_channel_reversed")

    @property
    def kodi_tv_show_collection(self) -> Preset:
        """
        Kodi TV Show from a collection of multiple URLs. TODO: finish docstring
        """
        return self._tv_show_collection(name="kodi_tv_show_collection")

    @property
    def kodi_tv_show_collection_reversed(self) -> Preset:
        """
        Kodi TV Show from a collection of multiple URLs. TODO: finish docstring
        """
        return self._tv_show_collection_reversed(name="kodi_tv_show_collection_reversed")
