Config
======
ytdl-sub is configured in the ``config.yaml`` and consists of two sections:

.. code-block:: yaml

   configuration:
   presets:


configuration
-------------

The ``configuration`` section contains app-wide configs.

presets
-------

``presets`` define a `formula` for how to format downloaded media and metadata.

source
^^^^^^
Download strategies dictate what exactly is getting downloaded from which
source. By having separate strategies, we can define strategy-dependent
parameters to better fine-tune how we download things.

youtube
"""""""

channel
'''''''
.. code-block:: yaml

   presets:
     my_example_preset:
       youtube:
         download_strategy: "channel"

channel_id
__________
  .. autoproperty:: ytdl_sub.downloaders.youtube_downloader.YoutubeChannelDownloaderOptions.channel_id

channel_avatar_path
___________________
  .. autoproperty:: ytdl_sub.downloaders.youtube_downloader.YoutubeChannelDownloaderOptions.channel_avatar_path

channel_banner_path
___________________
  .. autoproperty:: ytdl_sub.downloaders.youtube_downloader.YoutubeChannelDownloaderOptions.channel_banner_path

before
______
  .. autoproperty:: ytdl_sub.downloaders.youtube_downloader.YoutubeChannelDownloaderOptions.before

after
_____
  .. autoproperty:: ytdl_sub.downloaders.youtube_downloader.YoutubeChannelDownloaderOptions.after

--------

playlist
''''''''
.. code-block:: yaml

   presets:
     my_example_preset:
       youtube:
         download_strategy: "playlist"

playlist_id
___________
  .. autoproperty:: ytdl_sub.downloaders.youtube_downloader.YoutubePlaylistDownloaderOptions.playlist_id

--------

video
'''''
.. code-block:: yaml

   presets:
     my_example_preset:
       youtube:
         download_strategy: "video"

video_id
________
  .. autoproperty:: ytdl_sub.downloaders.youtube_downloader.YoutubeVideoDownloaderOptions.video_id

--------

soundcloud
""""""""""

albums_and_singles
''''''''''''''''''
.. code-block:: yaml

   presets:
     my_example_preset:
       soundcloud:
         download_strategy: "albums_and_singles"

username
________
  .. autoproperty:: ytdl_sub.downloaders.soundcloud_downloader.SoundcloudAlbumsAndSinglesDownloadOptions.username

skip_premiere_tracks
____________________
  .. autoproperty:: ytdl_sub.downloaders.soundcloud_downloader.SoundcloudAlbumsAndSinglesDownloadOptions.skip_premiere_tracks

--------

output_options
^^^^^^^^^^^^^^

output_directory
""""""""""""""""
  .. autoproperty:: ytdl_sub.config.preset_options.OutputOptions.output_directory

file_name
"""""""""
  .. autoproperty:: ytdl_sub.config.preset_options.OutputOptions.file_name

thumbnail_name
""""""""""""""
  .. autoproperty:: ytdl_sub.config.preset_options.OutputOptions.thumbnail_name

maintain_download_archive
"""""""""""""""""""""""""
  .. autoproperty:: ytdl_sub.config.preset_options.OutputOptions.maintain_download_archive

keep_files
""""""""""
  .. autoproperty:: ytdl_sub.config.preset_options.OutputOptions.keep_files

YTDL Options
^^^^^^^^^^^^
TODO

Overrides
^^^^^^^^^
TODO

Plugins
^^^^^^^

Music Tags
""""""""""
TODO

NFO
"""
TODO

NFO Output Directory
""""""""""""""""""""
TODO

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
