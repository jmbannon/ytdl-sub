Config
======
ytdl-sub is configured using a ``config.yaml`` file.

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

.. autoclass:: ytdl_sub.config.config_validator.ConfigOptions()
  :members:
  :member-order: bysource


presets
^^^^^^^
``presets`` define a `formula` for how to format downloaded media and metadata.

download_strategy
"""""""""""""""""
Download strategies dictate what is getting downloaded from a source. Each
download strategy has its own set of parameters.

.. _url:

url
'''
.. autoclass:: ytdl_sub.downloaders.generic.url.UrlDownloadOptions()
  :members: url, playlist_thumbnails, source_thumbnails
  :member-order: bysource

multi_url
'''''''''
.. autoclass:: ytdl_sub.downloaders.generic.multi_url.MultiUrlDownloadOptions()
  :members: urls, variables

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
     custom_preset:
       ...
     parent_preset:
       ...
     child_preset:
       preset: "parent_preset"

In the example above, ``child_preset`` inherits all fields defined in ``parent_preset``.
It is advantageous to use parent presets where possible to reduce duplicate yaml
definitions.

Presets also support inheritance from multiple presets:

.. code-block:: yaml

     child_preset:
       preset:
         - "custom_preset"
         - "parent_preset"

In this example, ``child_preset`` will inherit all fields from ``custom_preset``
and ``parent_preset`` in that order. The bottom-most preset has the highest
priority.

-------------------------------------------------------------------------------


Plugins
"""""""
Plugins are used to perform any type of post-processing to the already downloaded files.

audio_extract
'''''''''''''
.. autoclass:: ytdl_sub.plugins.audio_extract.AudioExtractOptions()
  :members:
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

chapters
''''''''
.. autoclass:: ytdl_sub.plugins.chapters.ChaptersOptions()
  :members:
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

date_range
''''''''''
.. autoclass:: ytdl_sub.plugins.date_range.DateRangeOptions()
  :members:
  :member-order: bysource
  :exclude-members: partial_validate

file_convert
''''''''''''
.. autoclass:: ytdl_sub.plugins.file_convert.FileConvertOptions()
  :members:
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

music_tags
''''''''''
.. autoclass:: ytdl_sub.plugins.music_tags.MusicTagsOptions()
  :members:
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

nfo_tags
''''''''
.. autoclass:: ytdl_sub.plugins.nfo_tags.NfoTagsOptions()
  :members: nfo_name, nfo_root, tags, kodi_safe
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

output_directory_nfo_tags
'''''''''''''''''''''''''
.. autoclass:: ytdl_sub.plugins.output_directory_nfo_tags.OutputDirectoryNfoTagsOptions()
  :members: nfo_name, nfo_root, tags, kodi_safe
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

regex
'''''
.. autoclass:: ytdl_sub.plugins.regex.RegexOptions()
  :members: skip_if_match_fails

.. autoclass:: ytdl_sub.plugins.regex.SourceVariableRegex()
  :members: match, capture_group_names, capture_group_defaults
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

split_by_chapters
'''''''''''''''''
.. autoclass:: ytdl_sub.plugins.split_by_chapters.SplitByChaptersOptions()
  :members: when_no_chapters
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

subtitles
'''''''''
.. autoclass:: ytdl_sub.plugins.subtitles.SubtitleOptions()
  :members: subtitles_name, subtitles_type, embed_subtitles, languages, allow_auto_generated_subtitles
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

video_tags
''''''''''
.. autoclass:: ytdl_sub.plugins.video_tags.VideoTagsOptions()
  :members:
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

.. _subscription_yaml:

subscription.yaml
-----------------
The ``subscription.yaml`` file is where we use our `presets`_ in the `config.yaml`_
to define a `subscription`: something we want to recurrently download such as a specific
channel or playlist.

The only difference between a ``subscription`` and ``preset`` is that the subscription
must have all required fields and ``{variables}`` defined so it can perform a download.

Below is an example that downloads a YouTube playlist:

.. code-block:: yaml
  :caption: config.yaml

   presets:
     playlist_preset_ex:
       download:
         download_strategy: "url"
         url: "{url}"
       output_options:
         output_directory: "{output_directory}/{playlist_name}"
         file_name: "{playlist_name}.{title}.{ext}"
       overrides:
         output_directory: "/path/to/ytdl-sub-videos"

.. code-block:: yaml
  :caption: subscription.yaml

   my_subscription_name:
     preset: "playlist_preset_ex"
     overrides:
       playlist_name: "diy-playlist"
       url: "https://youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg"

Our preset ``playlist_preset_ex`` defines three
custom variables: ``{output_directory}``, ``{playlist_name}``, and ``{url}``. The subscription sets
the `parent preset`_ to ``playlist_preset_ex``, and must define the variables ``{playlist_name}``
and ``{url}`` since the preset did not.

File Preset
^^^^^^^^^^^
You can apply a preset to all subscriptions in the ``subscription.yaml`` file
by using the file-wide ``__preset__``:

.. code-block:: yaml
  :caption: subscription.yaml

   __preset__:
     preset: "playlist_preset_ex"

   my_subscription_name:
     overrides:
       url: "https://youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg"
       playlist_name: "diy-playlist"

This ``subscription.yaml`` is equivalent to the one above it because all
subscriptions automatically set ``__preset__`` as a `parent preset`_.

-------------------------------------------------------------------------------

.. _source-variables:

Source Variables
----------------

.. autoclass:: ytdl_sub.entries.variables.entry_variables.EntryVariables
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