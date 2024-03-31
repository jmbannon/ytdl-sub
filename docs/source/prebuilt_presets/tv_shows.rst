===============
TV Show Presets
===============

Player-Specific Presets
=======================

``ytdl-sub`` provides player-specific versions of certain presets, which apply settings to optimize the downloads for that player.

The following actions are taken based on the indicated player:


Jellyfin
--------
* Places any season-specific poster art in the main show folder
* Generates NFO tags

Kodi
--------
* Everything that the Jellyfin version does
* Enables ``kodi_safe`` NFOs, replacing 4-byte unicode characters that break kodi with ``□``

Plex
--------
* :ref:`Special sanitization <config_reference/scripting/entry_variables:title_sanitized_plex>` of numbers so Plex doesn't recognize numbers that are part of the title as the episode number
* Converts all downloaded videos to the mp4 format
* Places any season-specific poster art into the season folder

----------------------------------------------

Generic Presets
===============

There are two main methods for downloading and formatting videos as a TV show.

TV Show by Date
---------------

TV Show by Date will organize something like a YouTube channel or playlist into a tv show, where seasons and episodes are organized using upload date.

Example
~~~~~~~
Must define ``tv_show_directory``. Available presets:

* ``"Kodi TV Show by Date"``
* ``"Jellyfin TV Show by Date"``
* ``"Plex TV Show by Date"``

.. code-block:: yaml

   __preset__:
     overrides:
       tv_show_directory: "/tv_shows"

   Plex TV Show by Date:

     # Sets genre tag to "Documentaries"
     = Documentaries:
       "NOVA PBS": "https://www.youtube.com/@novapbs"
       "National Geographic": "https://www.youtube.com/@NatGeo"
       "Cosmos - What If": "https://www.youtube.com/playlist?list=PLZdXRHYAVxTJno6oFF9nLGuwXNGYHmE8U"

     # Sets genre tag to "Kids", "TV-Y" for content rating
     = Kids | = TV-Y:
       "Jake Trains": "https://www.youtube.com/@JakeTrains"
       "Kids Toys Play": "https://www.youtube.com/@KidsToysPlayChannel"

     = Music:
       # TV show subscriptions can support multiple urls and store in the same TV Show
       "Rick Beato":
         - "https://www.youtube.com/@RickBeato"
         - "https://www.youtube.com/@rickbeato240"

Advanced Usage
~~~~~~~~~~~~~~

If you prefer a different organization method, you can instead apply multiple presets to your subscriptions.

You will need a base of one of the below:

* ``kodi_tv_show_by_date``
* ``jellyfin_tv_show_by_date``
* ``plex_tv_show_by_date``

And then add one of these:

* ``season_by_year__episode_by_month_day``
* ``season_by_year_month__episode_by_day``
* ``season_by_year__episode_by_month_day_reversed``
  
  * Episode numbers are reversed, meaning more recent episodes appear at the top of a season by having a lower value.
* ``season_by_year__episode_by_download_index``
  
  * Episodes are numbered by the download order. NOTE that this is fetched using the length of the download archive. Do not use if you intend to remove old videos.


TV Show Collection
------------------

TV Show Collections set each URL as its own season. If a video belongs to multiple URLs
(i.e. a channel and a channel's playlist), the video will only download once and reside in
the higher-numbered season.

Two main use cases of a collection are:
   1. Organize a YouTube channel TV show where Season 1 contains any video
      not in a 'season playlist', Season 2 for 'Playlist A', Season 3 for
      'Playlist B', etc.
   2. Organize one or more YouTube channels/playlists, where each season
      represents a separate channel/playlist.

Example
~~~~~~~
Must define ``tv_show_directory``. Available presets:

* ``"Kodi TV Show Collection"``
* ``"Jellyfin TV Show Collection"``
* ``"Plex TV Show Collection"``

.. code-block:: yaml

   __preset__:
     overrides:
       tv_show_directory: "/tv_shows"

   Plex TV Show Collection:
     = Music:
       # Prefix with ~ to set specific override variables
       "~Beyond the Guitar":
         s01_name: "Videos"
         s01_url: "https://www.youtube.com/c/BeyondTheGuitar"
         s02_name: "Covers"
         s02_url: "https://www.youtube.com/playlist?list=PLE62gWlWZk5NWVAVuf0Lm9jdv_-_KXs0W"

Advanced Usage
~~~~~~~~~~~~~~

If you prefer a different organization method, you can instead apply multiple presets to your subscriptions.

You will need a base of one of the below:

* ``kodi_tv_show_collection``
* ``jellyfin_tv_show_collection``
* ``plex_tv_show_collection``

And then add one of these:

* ``season_by_collection__episode_by_year_month_day``
* ``season_by_collection__episode_by_year_month_day_reversed``
* ``season_by_collection__episode_by_playlist_index``
  
  * Only use playlist_index episode formatting for playlists that will be fully downloaded once and never again. Otherwise, indices can change.
* ``season_by_collection__episode_by_playlist_index_reversed``
