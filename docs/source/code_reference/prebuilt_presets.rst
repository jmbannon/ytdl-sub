================
Prebuilt Presets
================
If you are ready to start downloading, see our
`examples directory <https://github.com/jmbannon/ytdl-sub/tree/master/examples>`_
for ready-to-use configs and subscriptions. Read through them carefully before use.

Helper Presets
==============

By themselves, these presets won't get your media downloaded, but they're useful for condensing multi-line modifications to other presets into a single line through :ref:`guides/getting_started/advanced_configuration:preset inheritance`.

best_video_quality
------------------

This preset:
  ``1`` Is named ``best_video_quality``

  ``2`` Searches for the best video and audio formats available to download

  ``4`` Uses the ``mp4`` extension when merging multiple formats into one file

.. code-block:: yaml
  :linenos:

  best_video_quality:
    format: "bestvideo+bestaudio/best"
    ytdl_options:
      merge_output_format: "mp4"

max_1080p
---------

This preset:
  ``1`` Is named ``max_1080p``

  ``2`` Searches for the best video (up to 1080p) and audio formats to download

  ``4`` Uses the ``mp4`` extension when merging multiple formats into one file


.. code-block:: yaml
  :linenos:

  max_1080p:
    format: "(bv*[height<=1080]+bestaudio/best[height<=1080])"
    ytdl_options:
      merge_output_format: "mp4"

chunk_initial_download
----------------------

This preset:
  ``1`` Is named ``chunk_initial_download``

  ``3`` Downloads up to 20 videos per subscription per run

  ``4`` Reverses the subscription playlist, which starts from the beginning of the playlist in most cases

  ``5`` Will not stop downloading videos when it reaches a video that exists, but will skip the existing videos instead of redownloading them

  ``6`` Will stop downloading videos if a yt-dlp reject occurs

.. code-block:: yaml
  :linenos:

  chunk_initial_download:
    ytdl_options:
      max_downloads: 20
      playlistreverse: True
      break_on_existing: False
      break_on_reject: True

Only Recent
-----------

This preset:
  ``1`` Is named "Only Recent"
  
  ``3`` Only attempts to download videos uploaded after ``today-{only_recent_date_range}``, where ``{only_recent_date_range}`` is set as an override variable in your subscription or a :ref:`child preset <guides/getting_started/advanced_configuration:preset inheritance>`.

.. code-block:: yaml
  :linenos:

  "Only Recent":
    date_range:
      after: "today-{only_recent_date_range}"