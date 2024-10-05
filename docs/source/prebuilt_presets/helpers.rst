==============
Helper Presets
==============

.. hint::

   Apply presets to your subscriptions using pipes:

   .. code-block:: yaml
     :caption: Pipes can separate presets and values to apply them to all subscriptions below them.

     Plex TV Show by Date | best_video_quality:

       = Documentaries | chunk_initial_download:
         "NOVA PBS": "https://www.youtube.com/@novapbs"
         "National Geographic": "https://www.youtube.com/@NatGeo"

       = Documentaries:
         "Cosmos - What If": "https://www.youtube.com/playlist?list=PLZdXRHYAVxTJno6oFF9nLGuwXNGYHmE8U"

Common presets are not usable by themselves- setting one of these as the sole preset of your subscription and attempting to download will not work. But you can add these presets to quickly modify an existing preset to better suit your needs.

Best A/V Quality
----------------

Add the following preset to download the best available video and audio quality, and remux it into an MP4 container:

``best_video_quality``


Max 1080p Video
---------------

Add the following preset to download the best available audio and video quality, with the video not greater than 1080p, and remux it into an MP4 container:

``max_1080p``

Filter Keywords
---------------

Include or exclude media with any of the listed keywords in their titles. Both keywords and title/description are lower-cased before filtering.

``Filter Keywords``

.. tip::

   Use the `~` tilda subscription mode to set a subscription's list override variables.
   Tilda mode allows override variables to be set directly underneath it.

   .. code-block:: yaml
     Plex TV Show by Date:

       = Documentaries:
         "~NOVA PBS":
           url: "https://www.youtube.com/@novapbs"
           title_exclude_keywords:
             - "preview"
             - "trailer"

         "~To Catch a Smuggler":
           url: "https://www.youtube.com/@NatGeo"
           title_include_keywords:
             - "To Catch a Smuggler"


Chunk Initial Download
----------------------

If you are archiving a large channel, ``ytdl-sub`` will try pulling each video's metadata from newest to oldest before starting any downloads. It is a long process and not ideal. A better method is to chunk the process by using the following preset:

``chunk_initial_download``

It will download videos starting from the oldest one, and only download 20 at a time. You can
change this number by setting:

.. code-block:: yaml

  ytdl_options:
    max_downloads: 30  # Desired number to download per invocation

Once the entire channel is downloaded, remove this preset. Then it will pull metadata from newest to oldest again, and stop pulling additional metadata once it reaches a video that has already been downloaded.