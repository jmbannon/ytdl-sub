===============
TV Show Presets
===============


Player-Specific Presets
-----------------------

``ytdl-sub`` provides player-specific versions of certain presets, which apply settings
to optimize the downloads for that player.

The following actions are taken based on the indicated player:

Kodi
~~~~

* Everything that the Jellyfin version does
* Enables ``kodi_safe`` NFOs, replacing 4-byte unicode characters that break kodi with
  ``□``

Jellyfin
~~~~~~~~

* Places any season-specific poster art in the main show folder
* Generates NFO tags

Emby
~~~~

* Places any season-specific poster art in the main show folder
* Generates NFO tags

  * For named seasons, creates a ``season.nfo`` file per season

Plex
~~~~~~~~

* :ref:`Special sanitization
  <config_reference/scripting/entry_variables:title_sanitized_plex>` of numbers so Plex
  doesn't recognize numbers that are part of the title as the episode number
* Converts all downloaded videos to the mp4 format
* Places any season-specific poster art into the season folder

----------------------------------------------


TV Show by Date
---------------

TV Show by Date will organize something like a YouTube channel or playlist into a tv
show, where seasons and episodes are organized using upload date.

Example
~~~~~~~

Must define ``tv_show_directory``. Available presets:

* ``Kodi TV Show by Date``
* ``Jellyfin TV Show by Date``
* ``Emby TV Show by Date``
* ``Plex TV Show by Date``

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

If you prefer a different season/episode organization method, you can set the following
override variables.

.. code-block:: yaml

   __preset__:
     overrides:
       tv_show_directory: "/tv_shows"
       tv_show_by_date_season_ordering: "upload-year-month"
       tv_show_by_date_episode_ordering: "upload-day"

Or for a specific preset

.. code-block:: yaml

       "~Kids Toys Play":
          url: "https://www.youtube.com/@KidsToysPlayChannel"
          tv_show_by_date_season_ordering: "upload-year-month"
          tv_show_by_date_episode_ordering: "upload-day"

The following are supported. Be sure the combined season + episode ordering include the
year, month, day, i.e. upload-year + upload-month-day.

Season Ordering
"""""""""""""""

``tv_show_by_date_season_ordering`` supports one of the following:

* ``upload-year`` (default)
* ``upload-year-month``
* ``release-year``
* ``release-year-month``

Episode Ordering
""""""""""""""""

``tv_show_by_date_episode_ordering`` supports one of the following:

* ``upload-month-day`` (default)
* ``upload-month-day-reversed``

  * Reversed means more recent episodes appear at the top of a season by having a lower
    value.
* ``upload-day``
* ``release-day``
* ``release-month-day``
* ``release-month-day-reversed``
* ``download-index``

  * Episodes are numbered by the download order. **NOTE**: this is fetched using the
    length of the download archive. Do not use if you intend to remove old videos.

TV Show by Date presets use the following for defaults:

.. code-block:: yaml

   tv_show_by_date_season_ordering: "upload-year"
   tv_show_by_date_episode_ordering: "upload-month-day"

TV Show Collection
------------------

TV Show Collections set each URL as its own season. If a video belongs to multiple URLs
(i.e. a channel and a channel's playlist), the video will only download once and reside
in the higher-numbered season.

Two main use cases of a collection are:
   1. Organize a YouTube channel TV show where Season 1 contains any video not in a
      'season playlist', Season 2 for 'Playlist A', Season 3 for 'Playlist B', etc.
   2. Organize one or more YouTube channels/playlists, where each season represents a
      separate channel/playlist.

Today, ytdl-supports up to 40 seasons with 11 URLs per season.

Example
~~~~~~~

Must define ``tv_show_directory``. Available presets:

* ``Kodi TV Show Collection``
* ``Jellyfin TV Show Collection``
* ``Emby TV Show Collection``
* ``Plex TV Show Collection``

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

Other notable features include:

* TV show poster info is pulled from the first URL in s01.
* Duplicate videos in different URLs (channel /videos vs playlist) will not download twice.

  * The video will attributed to the season with the highest number.
* Individual seasons support both single and multi URL.
* s00 is supported for specials.

.. code-block:: yaml

       "~Beyond the Guitar":
         s00_name: "Specials"
         s00_url:
           - "https://www.youtube.com/watch?v=vXzguOdulAI"
           - "https://www.youtube.com/watch?v=IGwYDvaGAz0"
         s01_name: "Videos"
         s01_url:
           - "https://www.youtube.com/c/BeyondTheGuitar"
           - "https://www.youtube.com/@BeyondTheGuitarAcademy"
         s02_name: "Covers"
         s02_url: "https://www.youtube.com/playlist?list=PLE62gWlWZk5NWVAVuf0Lm9jdv_-_KXs0W"

Advanced Usage
~~~~~~~~~~~~~~

If you prefer a different episode organization method, you can set the following
override variables.

.. code-block:: yaml

   __preset__:
     overrides:
       tv_show_directory: "/tv_shows"
       tv_show_collection_episode_ordering: "release-year-month-day"

Or for a specific preset

.. code-block:: yaml

       "~Beyond the Guitar":
         tv_show_collection_episode_ordering: "release-year-month-day"
         s01_name: "Videos"
         s01_url: "https://www.youtube.com/c/BeyondTheGuitar"
         s02_name: "Covers"
         s02_url: "https://www.youtube.com/playlist?list=PLE62gWlWZk5NWVAVuf0Lm9jdv_-_KXs0W"


The following are supported.

Episode Ordering
""""""""""""""""

``tv_show_collection_episode_ordering`` supports one of the following:

* ``upload-year-month-day`` (default)
* ``upload-year-month-day-reversed``
* ``release-year-month-day``
* ``release-year-month-day-reversed``
* ``playlist-index``

  * Only use ``playlist-index`` episode formatting for playlists that will be fully
    downloaded once and never again. Otherwise, indices can change.
* ``playlist-index-reversed``

TV Show Collection presets use upload-year-month-day as the default.
