from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.entries.variables.entry_variables import pad

Preset = Dict[str, Any]

####################################################
# TV SHOW TYPES

KODI_TV_SHOW = "kodi_tv_show"
JELLYFIN_TV_SHOW = "jellyfin_tv_show"
PLEX_TV_SHOW = "plex_tv_show"

#####################################################
# TV SHOW URL PRESETS

TV_SHOW_URL = "tv_show_url"

SEASON_YEAR__EPISODE_MONTH_DAY = "season_by_year__episode_by_month_day"
SEASON_YEAR__EPISODE_MONTH_DAY_REVERSED = "season_by_year__episode_by_month_day_reversed"
SEASON_YEAR_MONTH__EPISODE_DAY = "season_by_year_month__episode_by_day"

#####################################################
# TV SHOW COLLECTION PRESETS

TV_SHOW_COLLECTION = "tv_show_collection"

SEASON_COLLECTION__EPISODE_Y_M_D = "season_by_collection__episode_by_year_month_day"
SEASON_COLLECTION__EPISODE_Y_M_D_REV = "season_by_collection__episode_by_year_month_day_reversed"


class PrebuiltPresets:
    @classmethod
    def _build_preset(cls, name: str, parent_presets: List[str]) -> Preset:
        return {"presets": {name: {"preset": parent_presets}}}

    @classmethod
    def _document_preset(cls) -> Preset:
        return {}

    @classmethod
    def get_preset_names(cls) -> Set[str]:
        preset_names = [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property)]
        return set(preset_names)

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


class PrebuiltTvShowUrlEpisodeOrderingPresets(PrebuiltPresets):
    @property
    def season_by_year__episode_by_month_day(self) -> Preset:
        """
        DOC
        """
        return self._document_preset()

    @property
    def season_by_year__episode_by_month_day_reversed(self) -> Preset:
        """
        DOC
        """
        return self._document_preset()

    @property
    def season_by_year_month__episode_by_day(self) -> Preset:
        """
        DOC
        """
        return self._document_preset()


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


class PrebuiltTvShowCollectionEpisodeOrderingPresets(PrebuiltPresets):
    @property
    def season_by_collection__episode_by_year_month_day(self) -> Preset:
        """
        DOC
        """
        return self._document_preset()

    @property
    def season_by_collection__episode_by_year_month_day_reversed(self) -> Preset:
        """
        DOC
        """
        return self._document_preset()


class PrebuiltTvShowCollectionSeasonPresets(PrebuiltPresets):
    @property
    def collection_season_1(self):
        """
        DOC
        """
        return self._document_preset()

    @property
    def collection_season_2(self):
        """
        DOC
        """
        return self._document_preset()

    @property
    def collection_season_3(self):
        """
        DOC
        """
        return self._document_preset()

    @property
    def collection_season_4(self):
        """
        DOC
        """
        return self._document_preset()

    @property
    def collection_season_5(self):
        """
        DOC
        """
        return self._document_preset()
