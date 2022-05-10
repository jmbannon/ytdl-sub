Config
======
ytdl-sub is configured using a ``config.yaml`` file. You can view our
:doc:`examples <examples>` and read detailed documentation for every configurable
field below.

config.yaml
-----------

The ``config.yaml`` is made up of two sections:

.. code-block:: yaml

   configuration:
   presets:

You can jump to any section and subsection of the config using the navigation
section to the left.

configuration
^^^^^^^^^^^^^
The ``configuration`` section contains app-wide configs applied to all presets
and subscriptions.

presets
^^^^^^^
``presets`` define a `formula` for how to format downloaded media and metadata.

download_strategy
"""""""""""""""""
Download strategies dictate what is getting downloaded from a source. Each
download strategy has its own set of parameters.

youtube
'''''''
Download strategies for downloading videos (or audio if you configure `ytdl_options`_ correctly) from Youtube. See
Download strategies for downloading music from Soundcloud. See
:class:`Youtube Variables <ytdl_sub.entries.variables.youtube_variables>`
for available source variables to use.

channel
_______
.. autoclass:: ytdl_sub.downloaders.youtube_downloader.YoutubeChannelDownloaderOptions()
  :members:
  :member-order: bysource
  :inherited-members:
  :exclude-members: get_date_range

-------------------------------------------------------------------------------

playlist
________
.. autoclass:: ytdl_sub.downloaders.youtube_downloader.YoutubePlaylistDownloaderOptions()
  :members:
  :member-order: bysource
  :inherited-members:

-------------------------------------------------------------------------------

video
_____
.. autoclass:: ytdl_sub.downloaders.youtube_downloader.YoutubeVideoDownloaderOptions()
  :members:
  :member-order: bysource
  :inherited-members:

-------------------------------------------------------------------------------

soundcloud
''''''''''
Download strategies for downloading music from Soundcloud. See
:class:`Soundcloud Variables <ytdl_sub.entries.variables.soundcloud_variables>`
for available source variables to use.

albums_and_singles
__________________
.. autoclass:: ytdl_sub.downloaders.soundcloud_downloader.SoundcloudAlbumsAndSinglesDownloadOptions()
  :members:
  :member-order: bysource
  :inherited-members:

-------------------------------------------------------------------------------

output_options
""""""""""""""

.. autoclass:: ytdl_sub.config.preset_options.OutputOptions()
  :members:
  :member-order: bysource

-------------------------------------------------------------------------------

ytdl_options
""""""""""""
.. autoclass:: ytdl_sub.config.preset_options.YTDLOptions()

-------------------------------------------------------------------------------

.. _overrides:

overrides
"""""""""
.. autoclass:: ytdl_sub.config.preset_options.Overrides()

-------------------------------------------------------------------------------


Plugins
"""""""
Plugins are used to perform any type of post-processing to the already downloaded files.

music_tags
''''''''''
.. autoclass:: ytdl_sub.plugins.music_tags.MusicTagsOptions()
  :members:

-------------------------------------------------------------------------------

nfo
'''
.. autoclass:: ytdl_sub.plugins.nfo_tags.NfoTagsOptions()
  :members:
  :member-order: bysource

-------------------------------------------------------------------------------

nfo_output_directory
''''''''''''''''''''
.. autoclass:: ytdl_sub.plugins.output_directory_nfo_tags.OutputDirectoryNfoTagsOptions()
  :members:
  :member-order: bysource

-------------------------------------------------------------------------------

.. _source-variables:

Source Variables
----------------

.. autoclass:: ytdl_sub.entries.variables.entry_variables.SourceVariables

.. _youtube-variables:

Youtube Variables
^^^^^^^^^^^^^^^^^
.. automodule:: ytdl_sub.entries.variables.youtube_variables
   :members:
   :inherited-members:
   :undoc-members:

.. _soundcloud-variables:

Soundcloud Variables
^^^^^^^^^^^^^^^^^^^^
.. automodule:: ytdl_sub.entries.variables.soundcloud_variables
   :members:
   :inherited-members:
   :undoc-members:

-------------------------------------------------------------------------------

Config Types
------------
The `config.yaml`_ uses various types for its configurable fields. Below is a definition for each type.

.. autoclass:: ytdl_sub.validators.string_formatter_validators.StringFormatterValidator()

.. autoclass:: ytdl_sub.validators.string_formatter_validators.OverridesStringFormatterValidator()

.. autoclass:: ytdl_sub.validators.string_datetime.StringDatetimeValidator()

.. autoclass:: ytdl_sub.validators.string_formatter_validators.DictFormatterValidator()

.. autoclass:: ytdl_sub.validators.string_formatter_validators.OverridesDictFormatterValidator()