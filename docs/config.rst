Config
======
ytdl-sub is configured using a ``config.yaml`` file. You can view our
:doc:`examples <examples>` and read detailed documentation for every configurable
field below.

.. _config_yaml:

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

.. autoclass:: ytdl_sub.config.config_file.ConfigOptions()
  :members:
  :member-order: bysource


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
.. autoclass:: ytdl_sub.downloaders.youtube.channel.YoutubeChannelDownloaderOptions()
  :members:
  :member-order: bysource
  :inherited-members:
  :exclude-members: get_date_range

.. autofunction:: ytdl_sub.downloaders.youtube.channel.YoutubeChannelDownloader.ytdl_option_defaults()

-------------------------------------------------------------------------------

.. _YouTube Playlist:

playlist
________
.. autoclass:: ytdl_sub.downloaders.youtube.playlist.YoutubePlaylistDownloaderOptions()
  :members:
  :member-order: bysource
  :inherited-members:

.. autofunction:: ytdl_sub.downloaders.youtube.playlist.YoutubePlaylistDownloader.ytdl_option_defaults()

-------------------------------------------------------------------------------

video
_____
.. autoclass:: ytdl_sub.downloaders.youtube.video.YoutubeVideoDownloaderOptions()
  :members:
  :member-order: bysource
  :inherited-members:

.. autofunction:: ytdl_sub.downloaders.youtube.video.YoutubeVideoDownloader.ytdl_option_defaults()

-------------------------------------------------------------------------------

split_video
___________
.. autoclass:: ytdl_sub.downloaders.youtube.split_video.YoutubeSplitVideoDownloaderOptions()
  :members:
  :member-order: bysource
  :inherited-members:

.. autofunction:: ytdl_sub.downloaders.youtube.split_video.YoutubeSplitVideoDownloader.ytdl_option_defaults()

-------------------------------------------------------------------------------

merge_playlist
______________
.. autoclass:: ytdl_sub.downloaders.youtube.merge_playlist.YoutubeMergePlaylistDownloaderOptions()
  :members:
  :member-order: bysource
  :inherited-members:

.. autofunction:: ytdl_sub.downloaders.youtube.merge_playlist.YoutubeMergePlaylistDownloader.ytdl_option_defaults()

-------------------------------------------------------------------------------

soundcloud
''''''''''
Download strategies for downloading music from Soundcloud. See
:class:`Soundcloud Variables <ytdl_sub.entries.variables.soundcloud_variables>`
for available source variables to use.

albums_and_singles
__________________
.. autoclass:: ytdl_sub.downloaders.soundcloud.albums_and_singles.SoundcloudAlbumsAndSinglesDownloadOptions()
  :members:
  :member-order: bysource
  :inherited-members:

.. autofunction:: ytdl_sub.downloaders.soundcloud.albums_and_singles.SoundcloudAlbumsAndSinglesDownloader.ytdl_option_defaults()

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

audio_extract
'''''''''''''
.. autoclass:: ytdl_sub.plugins.audio_extract.AudioExtractOptions()
  :members:
  :member-order: bysource

-------------------------------------------------------------------------------

chapters
''''''''
.. autoclass:: ytdl_sub.plugins.chapters.ChaptersOptions()
  :members:
  :member-order: bysource

-------------------------------------------------------------------------------

music_tags
''''''''''
.. autoclass:: ytdl_sub.plugins.music_tags.MusicTagsOptions()
  :members:

-------------------------------------------------------------------------------

nfo_tags
''''''''
.. autoclass:: ytdl_sub.plugins.nfo_tags.NfoTagsOptions()
  :members:
  :member-order: bysource

-------------------------------------------------------------------------------

output_directory_nfo_tags
'''''''''''''''''''''''''
.. autoclass:: ytdl_sub.plugins.output_directory_nfo_tags.OutputDirectoryNfoTagsOptions()
  :members:
  :member-order: bysource

-------------------------------------------------------------------------------

regex
'''''
.. autoclass:: ytdl_sub.plugins.regex.RegexOptions()
  :members: skip_if_match_fails

.. autoclass:: ytdl_sub.plugins.regex.SourceVariableRegex()
  :members: match, capture_group_names, capture_group_defaults
  :member-order: bysource

-------------------------------------------------------------------------------

subtitles
'''''''''
.. autoclass:: ytdl_sub.plugins.subtitles.SubtitleOptions()
  :members: subtitles_name, subtitles_type, embed_subtitles, languages, allow_auto_generated_subtitles
  :member-order: bysource

-------------------------------------------------------------------------------

video_tags
''''''''''
.. autoclass:: ytdl_sub.plugins.video_tags.VideoTagsOptions()
  :members:

-------------------------------------------------------------------------------

.. _subscription_yaml:

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
       playlist_url: "https://youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg"
     overrides:
       playlist_name: "diy-playlist"

Our preset ``playlist_preset_ex`` uses the `YouTube Playlist`_ download strategy, and defines two
custom variables: ``{output_directory}`` and ``{playlist_name}``. The subscription sets
the `parent preset`_ to ``playlist_preset_ex``, and must define the ``playlist_url`` field and
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
   :exclude-members: source_variables

.. _soundcloud-variables:

Soundcloud Variables
^^^^^^^^^^^^^^^^^^^^
.. automodule:: ytdl_sub.entries.variables.soundcloud_variables
   :members:
   :inherited-members:
   :undoc-members:
   :exclude-members: source_variables

-------------------------------------------------------------------------------

Config Types
------------
The `config.yaml`_ uses various types for its configurable fields. Below is a definition for each type.

.. autoclass:: ytdl_sub.validators.string_formatter_validators.StringFormatterValidator()

.. autoclass:: ytdl_sub.validators.string_formatter_validators.OverridesStringFormatterValidator()

.. autoclass:: ytdl_sub.validators.string_datetime.StringDatetimeValidator()

.. autoclass:: ytdl_sub.validators.string_formatter_validators.DictFormatterValidator()

.. autoclass:: ytdl_sub.validators.string_formatter_validators.OverridesDictFormatterValidator()