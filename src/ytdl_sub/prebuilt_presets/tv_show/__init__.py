from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.entries.variables.entry_variables import pad

Preset = Dict[str, Any]

####################################################
# TV SHOW TYPES

KODI_TV_SHOW = "_kodi_tv_show"
JELLYFIN_TV_SHOW = "_jellyfin_tv_show"
PLEX_TV_SHOW = "_plex_tv_show"

#####################################################
# TV SHOW URL PRESETS

TV_SHOW_BY_DATE = "_tv_show_by_date"

SEASON_YEAR__EPISODE_MONTH_DAY = "season_by_year__episode_by_month_day"
SEASON_YEAR__EPISODE_MONTH_DAY_REVERSED = "season_by_year__episode_by_month_day_reversed"
SEASON_YEAR_MONTH__EPISODE_DAY = "season_by_year_month__episode_by_day"

#####################################################
# TV SHOW COLLECTION PRESETS

TV_SHOW_COLLECTION = "_tv_show_collection"

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
        """
        Returns
        -------
        Preset names in the set
        """
        preset_names = [prop for prop in dir(cls) if isinstance(getattr(cls, prop), property)]
        return set(preset_names)

    @classmethod
    def get_presets(cls) -> List[Preset]:
        """
        Returns
        -------
        Preset dicts in the set if they are not added in other yamls
        """
        return [getattr(cls(), preset_name) for preset_name in cls.get_preset_names()]


class TvShowByDatePresets(PrebuiltPresets):
    """
    TV Show by Date presets create a TV show from a single URL using upload dates as season/episode
    numbers.
    """

    @property
    def kodi_tv_show_by_date(self):
        """
        Formats a TV show organized by date for Kodi
        """
        return self._build_preset(
            name="kodi_tv_show_by_date", parent_presets=[KODI_TV_SHOW, TV_SHOW_BY_DATE]
        )

    @property
    def jellyfin_tv_show_by_date(self):
        """
        Formats a TV show organized by date for Jellyfin
        """
        return self._build_preset(
            name="jellyfin_tv_show_by_date", parent_presets=[JELLYFIN_TV_SHOW, TV_SHOW_BY_DATE]
        )

    @property
    def plex_tv_show_by_date(self):
        """
        Formats a TV show organized by date for Plex
        """
        return self._build_preset(
            name="plex_tv_show_by_date", parent_presets=[PLEX_TV_SHOW, TV_SHOW_BY_DATE]
        )


class TvShowByDateEpisodeFormattingPresets(PrebuiltPresets):
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


class TvShowCollectionPresets(PrebuiltPresets):
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


class TvShowCollectionEpisodeFormattingPresets(PrebuiltPresets):
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

    @property
    def season_by_collection__episode_by_playlist_index(self) -> Preset:
        """
        DOC
        """
        return self._document_preset()

    @property
    def season_by_collection__episode_by_playlist_index_reversed(self) -> Preset:
        """
        DOC
        """
        return self._document_preset()


class TvShowCollectionSeasonPresets(PrebuiltPresets):
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
