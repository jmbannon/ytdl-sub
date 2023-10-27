from ytdl_sub.prebuilt_presets import PrebuiltPresets


class TvShowByDatePresets(PrebuiltPresets):
    preset_names = {
        "Kodi TV Show by Date",
        "Jellyfin TV Show by Date",
        "Plex TV Show by Date",
    }


class TvShowByDateOldPresets(PrebuiltPresets):
    """
    TV Show by Date presets create a TV show from a single URL using upload dates as season/episode
    numbers.
    """

    preset_names = {
        "kodi_tv_show_by_date",
        "jellyfin_tv_show_by_date",
        "plex_tv_show_by_date",
    }


class TvShowByDateEpisodeFormattingPresets(PrebuiltPresets):
    preset_names = {
        "season_by_year__episode_by_month_day",
        "season_by_year__episode_by_month_day_reversed",
        "season_by_year_month__episode_by_day",
        "season_by_year__episode_by_download_index",
    }


class TvShowCollectionPresets(PrebuiltPresets):
    preset_names = {
        "kodi_tv_show_collection",
        "jellyfin_tv_show_collection",
        "plex_tv_show_collection",
    }


class TvShowCollectionEpisodeFormattingPresets(PrebuiltPresets):
    preset_names = {
        "season_by_collection__episode_by_year_month_day",
        "season_by_collection__episode_by_year_month_day_reversed",
        "season_by_collection__episode_by_playlist_index",
        "season_by_collection__episode_by_playlist_index_reversed",
    }


class TvShowCollectionSeasonPresets(PrebuiltPresets):
    preset_names = {
        "collection_season_1",
        "collection_season_2",
        "collection_season_3",
        "collection_season_4",
        "collection_season_5",
    }
