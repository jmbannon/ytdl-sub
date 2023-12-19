==================
Configuration File
==================
-----------
config.yaml
-----------

ytdl-sub is configured using a ``config.yaml`` file.

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
~~~~~~~~~~~~~
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
~~~~~~~
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