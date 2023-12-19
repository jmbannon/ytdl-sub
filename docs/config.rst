Config
======
ytdl-sub is configured using a ``config.yaml`` file.

.. _config:

config.yaml
-----------

The ``config.yaml`` is made up of two sections:

.. code-block:: yaml

   configuration:
   presets:

You can jump to any section and subsection of the config using the navigation
section to the left.

Note for Windows users, paths can be represented with ``C:/forward/slashes/like/linux``.
If you wish to represent paths like Windows, you will need to ``C:\\double\\bashslash\\paths``
in order to escape the backslash character.

configuration
^^^^^^^^^^^^^
The ``configuration`` section contains app-wide configs applied to all presets
and subscriptions.

.. autoclass:: ytdl_sub.config.config_validator.ConfigOptions()
  :members:
  :member-order: bysource
  :exclude-members: subscription_value, persist_logs, experimental

persist_logs
""""""""""""
Within ``configuration``, define whether logs from subscription downloads
should be persisted.

.. code-block:: yaml

   configuration:
     persist_logs:
       logs_directory: "/path/to/log/directory"

Log files are stored as
``YYYY-mm-dd-HHMMSS.subscription_name.(success|error).log``.

.. autoclass:: ytdl_sub.config.config_validator.PersistLogsValidator()
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
.. autoclass:: ytdl_sub.downloaders.url.url.UrlDownloadOptions()
  :members: url, playlist_thumbnails, source_thumbnails, download_reverse
  :member-order: bysource

multi_url
'''''''''
.. autoclass:: ytdl_sub.downloaders.url.multi_url.MultiUrlDownloadOptions()
  :members: urls, variables

-------------------------------------------------------------------------------

output_options
""""""""""""""

.. autoclass:: ytdl_sub.config.preset_options.OutputOptions()
  :members:
  :member-order: bysource
  :exclude-members: get_upload_date_range_to_keep, partial_validate

-------------------------------------------------------------------------------

.. _ytdl_options:

ytdl_options
""""""""""""
.. autoclass:: ytdl_sub.config.preset_options.YTDLOptions()

-------------------------------------------------------------------------------

.. _overrides:

overrides
"""""""""
.. autoclass:: ytdl_sub.config.overrides.Overrides()

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

If you are only inheriting from one preset, the syntax ``preset: "parent_preset"`` is
valid YAML. Inheriting from multiple presets require use of a list.

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

-------------------------------------------------------------------------------

embed_thumbnail
''''''''''''''''

.. autoclass:: ytdl_sub.plugins.embed_thumbnail.EmbedThumbnailOptions()

-------------------------------------------------------------------------------

file_convert
''''''''''''
.. autoclass:: ytdl_sub.plugins.file_convert.FileConvertOptions()
  :members:
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

format
''''''
.. autoclass:: ytdl_sub.plugins.format.FormatOptions()

-------------------------------------------------------------------------------

match_filters
'''''''''''''
.. autoclass:: ytdl_sub.plugins.match_filters.MatchFiltersOptions()
  :members:
  :member-order: bysource
  :exclude-members: partial_validate

-------------------------------------------------------------------------------

music_tags
''''''''''
.. autoclass:: ytdl_sub.plugins.music_tags.MusicTagsOptions()

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

.. autoclass:: ytdl_sub.plugins.regex.VariableRegex()
  :members: match, capture_group_names, capture_group_defaults, exclude
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

throttle_protection
'''''''''''''''''''
.. autoclass:: ytdl_sub.plugins.throttle_protection.ThrottleProtectionOptions()
  :members:
  :member-order: bysource

-------------------------------------------------------------------------------

video_tags
''''''''''
.. autoclass:: ytdl_sub.plugins.video_tags.VideoTagsOptions()

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

.. _beautifying subscriptions:

Beautifying Subscriptions
^^^^^^^^^^^^^^^^^^^^^^^^^
Subscriptions support using presets as keys, and using keys to set override variables as values.
For example:

.. code-block:: yaml
  :caption: subscription.yaml

   TV Show Full Archive:
     = News:
         "Breaking News": "https://www.youtube.com/@SomeBreakingNews"

   TV Show Only Recent:
     = Tech | TV-Y:
       "Two Minute Papers": "https://www.youtube.com/@TwoMinutePapers"

Will create two subscriptions named "Breaking News" and "Two Minute Papers", equivalent to:

.. code-block:: yaml

  "Breaking News":
    preset:
      - "TV Show Full Archive"

    overrides:
      subscription_indent_1: "News"
      subscription_name: "Breaking News"
      subscription_value: "https://www.youtube.com/@SomeBreakingNews"

  "Two Minute Papers":
    preset:
      - "TV Show Only Recent"

    overrides:
      subscription_indent_1: "Tech"
      subscription_indent_2: "TV-Y"
      subscription_name: "Two Minute Papers"
      subscription_value: "https://www.youtube.com/@TwoMinutePapers"

You can provide as many parent presets in the form of keys, and subscription indents as ``=keys``.
This can drastically simplify subscription definitions by setting things like so in your
parent preset:

.. code-block:: yaml

  presets:
    "TV Show Preset":
      overrides:
        subscription_indent_1: "default-genre"
        subscription_indent_2: "default-content-rating"

        tv_show_name: "{subscription_name}"
        url: "{subscription_value}"
        genre: "{subscription_indent_1}"
        content_rating: "{subscription_indent_2}"

.. _subscription value:

File Preset
^^^^^^^^^^^
NOTE: This is deprecated in favor of using the method in :ref:`beautifying subscriptions`.

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


Subscription Value
^^^^^^^^^^^^^^^^^^^
NOTE: This is deprecated in favor of using the method in :ref:`beautifying subscriptions`.

With a clever config and use of ``__preset__``, your subscriptions can typically boil
down to a name and url. You can set ``__value__`` to the name of an override variable,
and use the override variable ``subscription_name`` to achieve one-liner subscriptions.
Using the example above, we can do:

.. code-block:: yaml
  :caption: subscription.yaml

   __preset__:
     preset:
       - "tv_show"
     overrides:
       tv_show_name: "{subscription_name}"

   __value__: "url"

   # single-line subscription, sets "Brandon Acker" and the subscription value
   # to the override variables tv_show_name and url
   "Brandon Acker": "https://www.youtube.com/@brandonacker"

Traditional subscriptions that can override presets will still work when using ``__value__``.
``__value__`` can also be set within a :ref:`config`.

-------------------------------------------------------------------------------

.. _source-variables:

Source Variables
----------------

.. autoclass:: ytdl_sub.entries.script.variable_definitions.VariableDefinitions()
   :members:
   :inherited-members:
   :undoc-members:

Override Variables
------------------

.. autoclass:: ytdl_sub.entries.variables.override_variables.OverrideVariables()
   :members:
   :member-order: bysource

-------------------------------------------------------------------------------

Config Types
------------
The `config.yaml`_ uses various types for its configurable fields. Below is a definition for each type.

.. autoclass:: ytdl_sub.validators.string_formatter_validators.StringFormatterValidator()

.. autoclass:: ytdl_sub.validators.string_formatter_validators.OverridesStringFormatterValidator()

.. autoclass:: ytdl_sub.validators.file_path_validators.StringFormatterFileNameValidator()

.. autoclass:: ytdl_sub.validators.string_datetime.StringDatetimeValidator()

.. autoclass:: ytdl_sub.validators.string_formatter_validators.DictFormatterValidator()

.. autoclass:: ytdl_sub.validators.string_formatter_validators.OverridesDictFormatterValidator()
