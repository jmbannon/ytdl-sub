Configuration
=============
ytdl-sub is configured in the ``config.yaml`` and consists of two sections:

.. code-block:: yaml

   configuration:
   presets:

The ``configuration`` section contains app-wide configs.

Presets
-------

``presets`` define a `formula` for how to format downloaded media and metadata.

Required: Source Download Strategy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Download strategies dictate what exactly is getting downloaded from which
source. By having separate strategies, we can define strategy-dependent
parameters to better fine-tune how we download things.

youtube: channel
""""""""""""""""
.. code-block:: yaml

   presets:
     my_example_preset:
       youtube:
         download_strategy: "channel"

.. autoclass:: ytdl_sub.downloaders.youtube_downloader.YoutubeChannelDownloaderOptions()
   :members:
   :inherited-members:
   :member-order: bysource
   :exclude-members: get_date_range

youtube: playlist
"""""""""""""""""
.. code-block:: yaml

   presets:
     my_example_preset:
       youtube:
         download_strategy: "playlist"

.. autoclass:: ytdl_sub.downloaders.youtube_downloader.YoutubePlaylistDownloaderOptions()
   :members:
   :inherited-members:

youtube: video
""""""""""""""
.. code-block:: yaml

   presets:
     my_example_preset:
       youtube:
         download_strategy: "video"

.. autoclass:: ytdl_sub.downloaders.youtube_downloader.YoutubeVideoDownloaderOptions()
   :members:
   :inherited-members:

soundcloud: albums_and_singles
""""""""""""""""""""""""""""""
.. code-block:: yaml

   presets:
     my_example_preset:
       soundcloud:
         download_strategy: "albums_and_singles"

.. autoclass:: ytdl_sub.downloaders.soundcloud_downloader.SoundcloudAlbumsAndSinglesDownloadOptions()
   :members:
   :inherited-members:

Format Variables
----------------
Format variables are ``{variables}`` that contain metadata from downloaded
media.

.. contents:: Source Format Variables
   :local:

Youtube Variables
^^^^^^^^^^^^^^^^^

.. automodule:: ytdl_sub.entries.variables.youtube_variables
   :members:
   :inherited-members:
   :undoc-members:

Soundcloud Variables
^^^^^^^^^^^^^^^^^^^^

.. automodule:: ytdl_sub.entries.variables.soundcloud_variables
   :members:
   :inherited-members:
   :undoc-members:

