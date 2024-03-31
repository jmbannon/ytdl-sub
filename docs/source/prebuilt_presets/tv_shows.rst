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

Plug and Play Presets
~~~~~~~~~~~~~~~~~~~~~

You can use any of these presets in your ``subscriptions.yaml`` as a "One size fits all" solution- they should set all appropriate values. These will organize seasons by year and episodes by month, then day.

Must define ``tv_show_directory``

* ``"Kodi TV Show by Date"``
* ``"Jellyfin TV Show by Date"``
* ``"Plex TV Show by Date"``

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

An example of a subscription that will be played on Kodi, organized by year with the most recent episode at the top (having a lower episode number), with a genre of "Pop":

.. code-block:: yaml
  :caption: subscriptions.yaml

  __preset__:
    overrides:
      tv_show_directory: "/tv_shows"

  kodi_tv_show_by_date:
    season_by_year_episode_by_month_day_reversed:
      = Pop:
        "Rick A": "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"

You can also choose to combine multiple URLs into one show. This will result in your videos being downloaded to the same folder, and the episode numbers being shared between them (so you won't have two episode 10's, for example). Note that you may :ytdl-sub-gh:`experience issues <issues/833>` if you use more than 20 URLs at this time.

.. code-block:: yaml
  :caption: subscriptions.yaml

  __preset__:
    overrides:
      tv_show_directory: "/tv_shows"

  kodi_tv_show_by_date:
    season_by_year_episode_by_month_day_reversed:
      = Pop:
        "~Rick A": 
          url: "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"
          url2: "https://www.youtube.com/@just.rick_6"


TV Show Collection
------------------

TV Show Collections are made up of multiple URLs, where each URL is a season.
If a video belongs to multiple URLs (i.e. a channel and a channel's playlist),
it will resolve to the bottom-most season, as defined in the subscription.

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
  
  * Only use playlist_index episode formatting for playlists that will be fully downloaded once and never again. Otherwise, indices can change.
* ``season_by_collection__episode_by_playlist_index_reversed``


Example
~~~~~~~

A preset/subscription requires specifying a player and episode formatting
with the following override variables:

.. code-block:: yaml

  rick_a_tv_show_collection:
    preset:
      - "jellyfin_tv_show_collection"
      - "season_by_collection__episode_by_year_month_day_reversed"
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