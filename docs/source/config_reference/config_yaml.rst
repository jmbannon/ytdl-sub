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

This section is work-in-progress!

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

In this example, ``child_preset`` will inherit all fields from ``custom_preset`` and
``parent_preset`` in that order. The bottom-most preset has the highest priority. More
specifically, presets are merged using `mergedeep`_ via `a TYPESAFE_ADDITIVE merge`_,
which means:

- if two conflicting keys arent lists or mappings, overwrite the higher priority one
- otherwise, combine then re-evaluate

If you are only inheriting from one preset, the syntax ``preset: "parent_preset"`` is
valid YAML. Inheriting from multiple presets require use of a list.

.. _`mergedeep`:
   https://mergedeep.readthedocs.io/en/latest/
.. _`a TYPESAFE_ADDITIVE merge`:
   https://mergedeep.readthedocs.io/en/latest/index.html#merge-strategies
