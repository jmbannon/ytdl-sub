Basic Configuration
===================

A configuration file serves two purposes:

1. Set application-level functionality that is not specifiable in a subscription file.
  .. note::

   ytdl-sub does not require a configuration file. However,
   certain application settings may be desirable for tweak, such as setting
   ``working_directory`` to make ytdl-sub perform the initial download
   to an SSD drive.

2. Create custom presets.
  .. note::

    In the prior Initial Subscription examples, we leveraged the prebuilt preset
    ``Jellyfin TV Show by Date``. This preset is entirely built using the same
    YAML configuration system offered to users by using a configuration file.

The following section attempts to demystify and explain how to...

- Set an application setting
- Know whether or not custom presets are actually needed
- How to create a custom preset
- How to use a custom preset on subscriptions

-------------

how this works, and show-case how

.. code-block:: yaml
  :linenos:

  configuration:
    working_directory: ".ytdl-sub-working-directory"

  presets:
    TV Show:
      preset:
        - "Jellyfin TV Show by Date"
        - "Max 1080p"

      embed_thumbnail: True

      throttle_protection:
         sleep_per_download_s:
           min: 2.2
           max: 10.8
         sleep_per_subscription_s:
           min: 9.0
           max: 14.1
         max_downloads_per_subscription:
           min: 10
           max: 36

      overrides:
        tv_show_directory: "/tv_shows"

    TV Show Only Recent:
      preset:
        - "TV Show"
        - "Only Recent"


Configuration Section
---------------------

The :ref:`configuration <config_reference/config_yaml:Configuration File>` section sets
options for ytdl-sub execution. Most users should set the path where ``ytdl-sub``
temporarily stores downloaded data before assembling it and moving it into your
library. To avoid unnecessarily long large file renames, use a path on the same
filesystem as your library in the ``overrides: / *_directory:`` paths:


.. code-block:: yaml
  :lineno-start: 1

  configuration:
    working_directory: ".ytdl-sub-working-directory"


Preset Section
--------------

Underneath ``presets``, we define two custom presets with the names ``TV Show`` and ``TV
Show Only Recent``.

.. code-block:: yaml

  presets:
    TV Show:
      ...
    TV Show Only Recent:
      ...

The indentation example above shows how to define multiple presets.


Custom Preset Definition
------------------------

Before we break down the above ``TV Show`` preset, lets first outline a preset layout:

.. code-block:: yaml

    Preset Name:
      preset:
        ...

      plugin(s):
        ...

      overrides:
        ...

Presets can contain three important things:

1. ``preset`` section, which can inherit :ref:`prebuilt presets
   <config_reference/prebuilt_presets/index:Prebuilt Preset Reference>` or other presets
   defined in your config.
2. :ref:`Plugin definitions <config_reference/plugins:Plugins>`
3. :ref:`overrides <config_reference/plugins:overrides>`, which can override inherited
   preset variables

Presets do not have to define all of these, as we'll see in the ``TV Show Only Recent``
preset.

Inheriting Presets
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml
  :lineno-start: 5

    TV Show:
      preset:
        - "Jellyfin TV Show by Date"
        - "Max 1080p"

The following snippet shows that the ``TV Show`` preset will inherit all properties of
the prebuilt presets ``Jellyfin TV Show by Date`` and ``Max 1080p`` in that order.

Order matters for preset inheritance. Bottom-most presets will override ones above them.

It is highly advisable to use :ref:`prebuilt presets
<config_reference/prebuilt_presets/index:Prebuilt Preset Reference>` as a starting point
for custom preset building, as they do the work of preset building to ensure things show
as expected in their respective media players. Read on to see how to override prebuilt
preset specifics such as title.

Defining Plugins
~~~~~~~~~~~~~~~~

.. code-block:: yaml
  :lineno-start: 10

      embed_thumbnail: True

      throttle_protection:
         sleep_per_download_s:
           min: 2.2
           max: 10.8
         sleep_per_subscription_s:
           min: 9.0
           max: 14.1
         max_downloads_per_subscription:
           min: 10
           max: 36

Our ``TV Show`` sets two plugins, :ref:`throttle_protection
<config_reference/plugins:throttle_protection>` and :ref:`embed_thumbnail
<config_reference/plugins:embed_thumbnail>`. Each plugin's documentation shows the
respective fields that they support.

If an inherited preset defines the same plugin, the custom preset will use
'merge-and-append' strategy to combine their definitions. What this means is:

1. If the field is a map (i.e. has sub-params like ``sleep_per_download_s`` above) or
   array, it will try to merge them
2. If both the inherited preset and custom preset set the same exact field and value
   (i.e. ``embed_thumbnail``) the custom preset will overwrite it

Setting Override Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml
  :lineno-start: 23

      overrides:
        tv_show_directory: "/ytdl_sub_tv_shows"

All override variables reside underneath the :ref:`overrides
<config_reference/plugins:overrides>` section.

It is important to remember that individual subscriptions can override specific override
variables.  When defining variables in a preset, it is best practice to define them with
the intention that

1. All subscriptions will use its value them
2. Use them as placeholders to perform other logic, then have subscriptions or child
   presets define their specific value

For simplicity, we'll focus on (1) for now. The above snippet sets the
``tv_show_directory`` variable to a file path. This variable name is specific to the
prebuilt TV show presets.

See the :ref:`prebuilt preset reference
<config_reference/prebuilt_presets/index:Prebuilt Preset Reference>` to see all
available variables that are overridable.


Using Custom Presets in Subscriptions
--------------------------------------

Subscription files can use custom presets just like any other prebuilt preset.  Below
shows a complete subscription file using the above two custom presets.

.. code-block:: yaml

  TV Show:
    = Documentaries:
      "NOVA PBS": "https://www.youtube.com/@novapbs"

    = Kids | = TV-Y:
      "Jake Trains": "https://www.youtube.com/@JakeTrains"

  TV Show Only Recent:
    = News:
      "BBC News": "https://www.youtube.com/@BBCNews"

Notice how we do not need to define ``tv_show_directory`` in the ``__preset__`` section
like in prior examples. This is because our custom presets do the work of defining it.


Reference Custom Config in the CLI
----------------------------------

Be sure to tell ytdl-sub to use your config by using the argument ``--config
/path/to/config.yaml``.

If you run ytdl-sub in the same directory, and the config file is named ``config.yaml``,
it will use it by default.
