===============
TV Show Presets
===============

Player-Specific Presets
-----------------------

``ytdl-sub`` provides player-specific versions of certain presets, which apply settings to optimize the downloads for that player.

All of these players will have:


Jellyfin
~~~~~~~~
* Places any season-specific poster art in the show folder


Kodi
~~~~
* Turns on :ref:`config_reference/plugins:kodi_safe`, replacing characters that would break kodi with safer characters
* 



Plex
~~~~
* :ref:`Special sanitization <config_reference/scripting/entry_variables:title_sanitized_plex>` of numbers so Plex doesn't recognize numbers that are part of the title as the episode number
* Converts all downloaded videos to the mp4 format
* Places any season-specific poster art into the season folder





There are two main methods for downloading and formatting videos as a TV show.

TV Show by Date
---------------

TV Show by Date will organize something like a YouTube channel or playlist
into a tv show, where seasons and episodes are organized using upload date.

Player Presets
~~~~~~~~~~~~~~

* ``kodi_tv_show_by_date``
* ``jellyfin_tv_show_by_date``
* ``plex_tv_show_by_date``

Episode Formatting Presets
~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~

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
      # tv_show_genre: "ytdl-sub"
      # tv_show_content_rating: "TV-14"
      # episode_title: "{upload_date_standardized} - {title}"
      # episode_description: "{webpage_url}"

In addition, you can add additional URLs to create a single TV by using the override variables
``url2``, ``url3``, ..., ``url20``:

.. code-block:: yaml

    overrides:
      tv_show_name: "Rick A"
      tv_show_directory: "/path/to/youtube_shows"
      url: "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"
      url2: "https://www.youtube.com/@just.rick_6"


TV Show Collection
------------------

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
~~~~~~~~~~~~~~

* ``kodi_tv_show_collection``
* ``jellyfin_tv_show_collection``
* ``plex_tv_show_collection``

Episode Formatting Presets
~~~~~~~~~~~~~~~~~~~~~~~~~~

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
* ``...``
* ``collection_season_40``

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
      # tv_show_genre: "ytdl-sub"
      # episode_title: "{upload_date_standardized} - {title}"
      # episode_description: "{webpage_url}"