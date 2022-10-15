from typing import Set


class PrebuiltPreset:
    """placeholder"""


_ = PrebuiltPreset()


class PrebuiltPresets:
    @classmethod
    def get_preset_names(cls) -> Set[str]:
        """
        Returns
        -------
        Preset names in the set
        """
        return set(
            preset_name
            for preset_name in dir(cls)
            if isinstance(getattr(cls, preset_name), PrebuiltPreset)
        )


class TvShowByDatePresets(PrebuiltPresets):
    """
    TV Show by Date presets create a TV show from a single URL using upload dates as season/episode
    numbers.
    """

    kodi_tv_show_by_date = _
    jellyfin_tv_show_by_date = _
    plex_tv_show_by_date = _


class TvShowByDateEpisodeFormattingPresets(PrebuiltPresets):
    season_by_year__episode_by_month_day = _
    season_by_year__episode_by_month_day_reversed = _
    season_by_year_month__episode_by_day = _
    season_by_year__episode_by_download_index = _


class TvShowCollectionPresets(PrebuiltPresets):
    """
    Docstring for all TV SHOW URL presets
    """

    kodi_tv_show_collection = _
    jellyfin_tv_show_collection = _
    plex_tv_show_collection = _


class TvShowCollectionEpisodeFormattingPresets(PrebuiltPresets):
    season_by_collection__episode_by_year_month_day = _
    season_by_collection__episode_by_year_month_day_reversed = _
    season_by_collection__episode_by_playlist_index = _
    season_by_collection__episode_by_playlist_index_reversed = _


class TvShowCollectionSeasonPresets(PrebuiltPresets):
    collection_season_1 = _
    collection_season_2 = _
    collection_season_3 = _
    collection_season_4 = _
    collection_season_5 = _
