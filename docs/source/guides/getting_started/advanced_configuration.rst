Advanced Configuration
======================

If the :doc:`prebuilt presets </prebuilt_presets/index>` aren't suitable for your needs, you may want to set up an advanced configuration.

Layout of a Config file
-----------------------

The layout of the ``config.yaml`` file is relatively straightforward:

.. code-block:: yaml

  presets:

    preset_name:
      plugin1:
        plugin1_option1: value1

This creates a preset named ``preset_name``, which contains the made-up
:doc:`plugin </config_reference/plugins>` ``plugin1``. Under each plugin are its settings.
A preset can contain multiple plugins.

Preset Inheritance
------------------

You can modularize your presets via preset inheritance. For example,

.. code-block:: yaml

  presets:

    TV Show:
      preset:
        - "Jellyfin TV Show by Date"

      overrides:
        tv_show_directory: "/ytdl_sub_tv_shows"

    TV Show Only Recent:
      preset:
        - "TV Show"
        - "Only Recent"

      overrides:
        only_recent_date_range: "3weeks"

This creates two presets:

* ``TV Show``
   * Inherits the :doc:`prebuilt </prebuilt_presets/index>` ``Jellyfin TV Show by Date`` preset
   * Sets the output tv show directory
* ``TV Show Only Recent``
   * Inherits the ``TV Show`` preset made above it and the ``Only Recent`` prebuilt preset
   * Sets only_recent preset to only keep the last 3 weeks worth of videos

Inheritance makes it easy to extend existing presets to include logic for your specific needs.
