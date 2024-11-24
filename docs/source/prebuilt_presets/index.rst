================
Prebuilt Presets
================

``ytdl-sub`` offers a number of built-in presets using best practices for formatting
media in various players.

.. hint::

   Apply multiple presets to your subscriptions using pipes. Pipes can define multiple presets and values
   on the same line to apply to all subscriptions nested below them.

   .. code-block:: yaml
     :caption: Applies Max Video Quality preset to all TV shows, and Chunk Downloads preset to some

     Plex TV Show by Date | Max Video Quality:

       = Documentaries | Chunk Downloads:
         "NOVA PBS": "https://www.youtube.com/@novapbs"
         "National Geographic": "https://www.youtube.com/@NatGeo"

       = Documentaries:
         "Cosmos - What If": "https://www.youtube.com/playlist?list=PLZdXRHYAVxTJno6oFF9nLGuwXNGYHmE8U"


For advanced users, you can review the prebuilt preset
definitions :doc:`here </config_reference/prebuilt_presets/index>`.

.. toctree:: 
  :titlesonly:

  tv_shows
  music
  music_videos
  media_quality
  helpers