Presets
=======
``ytdl-sub`` offers a number of built-in presets using best practices for formatting
media in various players.

TV Shows
--------

There are two main methods for downloading and formatting videos as a TV show.

TV Show by Date
^^^^^^^^^^^^^^^

TV Show by Date will organize something like a YouTube channel or playlist
into a tv show, where seasons and episodes are organized using upload date.

Player Presets
""""""""""""""

* ``kodi_tv_show_by_date``
* ``jellyfin_tv_show_by_date``
* ``plex_tv_show_by_date``

Episode Formatting Presets
""""""""""""""""""""""""""

* ``season_by_year__episode_by_month_day``
* ``season_by_year_month__episode_by_day``
* ``season_by_year__episode_by_month_day_reversed``
   * Episode numbers are reversed, meaning more recent episodes appear at the
     top of a season by having a lower value.
* ``season_by_year__episode_by_download_index``
  * Episodes are numbered by the download order. NOTE that this fetched using
    the length of the download archive. Do not use if you intend to remove
    old videos.

Usage
"""""

A preset/subscription requires specifying a player and episode formatting preset
and overriding the following variables:

.. code-block:: yaml

   rick_a_tv_show_by_date:
     preset:
       - "jellyfin_tv_show_by_date"
       - "season_by_year__episode_by_month_day"
     overrides:
       # required
       tv_show_name: "Rick A"
       tv_show_directory: "/path/to/youtube_shows"
       url: "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"
       # can be modified from their default value
       # episode_title: "{upload_date_standardized} - {title}"
       # episode_description: "{webpage_url}"


TV Show Collection
^^^^^^^^^^^^^^^^^^

TV Show Collections are made up from multiple URLs, where each URL is a season.
If a video belongs to multiple URLs (i.e. a channel and a channel's playlist),
it will resolve to the bottom-most season.

Two main use cases of a collection are:
   1. Organize a YouTube channel TV show where Season 1 contains any video
      not in a 'season playlist', Season 2 for 'Playlist A', Season 3 for
      'Playlist B', etc.
   2. Organize one or more YouTube channels/playlists, where each season
      represents a separate channel/playlist.

Player Presets
""""""""""""""

* ``kodi_tv_show_collection``
* ``jellyfin_tv_show_collection``
* ``plex_tv_show_collection``

Episode Formatting Presets
""""""""""""""""""""""""""

* ``season_by_collection__episode_by_year_month_day``
* ``season_by_collection__episode_by_year_month_day_reversed``
* ``season_by_collection__episode_by_playlist_index``
   * Only use playlist_index episode formatting for playlists that
     will be fully downloaded once and never again. Otherwise,
     indices can change.
* ``season_by_collection__episode_by_playlist_index_reversed``

Season Presets
""""""""""""""

* ``collection_season_1``
* ``collection_season_2``
* ``collection_season_3``
* ``collection_season_4``
* ``collection_season_5``

Example
"""""""

A preset/subscription requires specifying a player, episode formatting, and
one or more season presets, with the following override variables:

.. code-block:: yaml

   rick_a_tv_show_collection:
     preset:
       - "jellyfin_tv_show_collection"
       - "season_by_collection__episode_by_year_month_day_reversed"
       - "collection_season_1"
       - "collection_season_2"
     overrides:
       # required
       tv_show_name: "Rick A"
       tv_show_directory: "/path/to/youtube_shows"
       collection_season_1_url: "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"
       collection_season_1_name: "All Videos"
       collection_season_2_url: "https://www.youtube.com/playlist?list=PLlaN88a7y2_plecYoJxvRFTLHVbIVAOoc"
       collection_season_2_name: "Official Music Videos"
       # can be modified from their default value
       # episode_title: "{upload_date_standardized} - {title}"
       # episode_description: "{webpage_url}"
