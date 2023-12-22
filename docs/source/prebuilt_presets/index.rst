Presets
=======

``ytdl-sub`` offers a number of built-in presets using best practices for formatting
media in various players. For advanced users, you can find the prebuilt preset
definitions :ytdl-sub-gh:`here <tree/8998861b497f692ce17c949f0c4c3530831085b1/src/ytdl_sub/prebuilt_presets>`.

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

Player Presets 2
""""""""""""""""

* ``kodi_tv_show_collection``
* ``jellyfin_tv_show_collection``
* ``plex_tv_show_collection``

Episode Formatting Presets 2
""""""""""""""""""""""""""""

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

Common
------

Common presets are applicable to any config.

Best Video Quality
^^^^^^^^^^^^^^^^^^

Add the following preset to download the best available video and audio quality, and remux
it into an MP4 container:

* ``best_video_quality``


Max 1080p
^^^^^^^^^^^^^^^^^^

Add the following preset to download the best available audio and video quality, with the video not greater than 1080p, and remux it into an MP4 container:

* ``max_1080p``

Chunk Initial Download
^^^^^^^^^^^^^^^^^^^^^^

If you are archiving a large channel, ``ytdl-sub`` will try pulling each video's metadata from
newest to oldest before starting any downloads. It is a long process and not ideal. A better method
is to chunk the process by using the following preset:

* ``chunk_initial_download``

It will download videos starting from the oldest one, and only download 20 at a time. You can
change this number by setting:

.. code-block:: yaml

  ytdl_options:
    max_downloads: 30  # Desired number to download per invocation

Once the entire channel is downloaded, remove this preset. Then it will pull metadata from newest to
oldest again, and stop pulling additional metadata once it reaches a video that has already been
downloaded.
