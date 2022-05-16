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

.. _YouTube Playlist:

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
  :exclude-members: get_upload_date_range_to_keep

-------------------------------------------------------------------------------

.. _ytdl_options:

ytdl_options
""""""""""""
.. autoclass:: ytdl_sub.config.preset_options.YTDLOptions()

-------------------------------------------------------------------------------

.. _overrides:

overrides
"""""""""
.. autoclass:: ytdl_sub.config.preset_options.Overrides()

.. _parent preset:

preset
""""""
Presets support inheritance by defining a parent preset:

.. code-block:: yaml

   presets:
     parent_preset:
       ...
     child_preset:
       preset: "parent_preset"

In the example above, ``child_preset`` inherits all fields defined in ``parent_preset``.
It is advantageous to use parent presets where possible to reduce duplicate yaml
definitions.

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

subscription.yaml
-----------------
The ``subscription.yaml`` file is where we use our `presets`_ in the `config.yaml`_
to define a `subscription`: something we want to recurrently download such as a specific
channel or playlist.

The only difference between a ``subscription`` and ``preset`` is that the subscription
must have all required fields and ``{variables}`` defined so it can perform a download.

Below is an example that downloads YouTube videos:

.. code-block:: yaml
  :caption: config.yaml

   presets:
     playlist_preset_ex:
       youtube:
         download_strategy: "playlist"
       output_options:
         output_directory: "{output_directory}/{playlist_name}"
         file_name: "{playlist_name}.{title}.{ext}"
       overrides:
         output_directory: "/path/to/ytdl-sub-videos"

.. code-block:: yaml
  :caption: subscription.yaml

   my_subscription_name:
     preset: "playlist_preset_ex"
     youtube:
       playlist_id: "UCsvn_Po0SmunchJYtttWpOxMg"
     overrides:
       playlist_name: "diy-playlist"

Our preset ``playlist_preset_ex`` uses the `YouTube Playlist`_ download strategy, and defines two
custom variables: ``{output_directory}`` and ``{playlist_name}``. The subscription sets
the `parent preset`_ to ``playlist_preset_ex``, and must define the ``playlist_id`` field and
the ``{playlist_name}`` variable since the preset did not.

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