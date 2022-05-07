Config
======
ytdl-sub is configured using a ``config.yaml`` file. You can view our
:doc:`examples <examples>` and read detailed documentation for every configurable
field below.

The ``config.yaml`` is made up of two sections:

.. code-block:: yaml

   configuration:
   presets:

You can jump to any section and subsection of the config using the navigation
section to the left.

configuration
-------------
The ``configuration`` section contains app-wide configs applied to all presets
and subscriptions.

presets
-------
``presets`` define a `formula` for how to format downloaded media and metadata.

download_strategy
^^^^^^^^^^^^^^^^^
Download strategies dictate what is getting downloaded from a source. Each
download strategy has its own set of parameters.

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

-------------------------------------------------------------------------------

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

-------------------------------------------------------------------------------

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

-------------------------------------------------------------------------------

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

-------------------------------------------------------------------------------

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

-------------------------------------------------------------------------------

ytdl_options
^^^^^^^^^^^^
.. autoclass:: ytdl_sub.config.preset_options.YTDLOptions()

-------------------------------------------------------------------------------

overrides
^^^^^^^^^
.. autoclass:: ytdl_sub.config.preset_options.Overrides()

Plugins
^^^^^^^

music_tags
""""""""""
.. autoclass:: ytdl_sub.plugins.music_tags.MusicTagsOptions()

nfo
"""
.. autoclass:: ytdl_sub.plugins.nfo_tags.NfoTagsOptions()

nfo_output_directory
""""""""""""""""""""
.. autoclass:: ytdl_sub.plugins.output_directory_nfo_tags.OutputDirectoryNfoTagsOptions()

Source Variables
----------------
Source variables are ``{variables}`` that contain metadata from downloaded media.
These variables can be used in StringFormatters, but not OverrideFormatters.

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

Formatters
----------
Formatters are strings that can contain ``{variables}`` that are overwritten at
run-time with values assigned to that variable. There are two different types of
formatters.

String Formatter
^^^^^^^^^^^^^^^^
.. autoclass:: ytdl_sub.validators.string_formatter_validators.StringFormatterValidator()

Overrides Formatter
^^^^^^^^^^^^^^^^^^^
.. autoclass:: ytdl_sub.validators.string_formatter_validators.OverridesStringFormatterValidator()
