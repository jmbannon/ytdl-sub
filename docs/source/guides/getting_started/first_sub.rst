Initial Subscription
====================

Your first subscription file should look something like this:

.. code-block:: yaml
  :linenos:
  
  __preset__:
    overrides:
      tv_show_directory: "/tv_shows"
      music_directory: "/music"

  # Can choose between:
  #  - Plex TV Show by Date:
  #  - Jellyfin TV Show by Date:
  #  - Kodi TV Show by Date:
  #
  Jellyfin TV Show by Date:
    = Documentaries:
      "NOVA PBS": "https://www.youtube.com/@novapbs"

    = Kids | = TV-Y:
      "Jake Trains": "https://www.youtube.com/@JakeTrains"

  YouTube Releases:
    = Jazz:  # Sets genre tag to "Jazz"
      "Thelonious Monk": "https://www.youtube.com/@theloniousmonk3870/releases"

  YouTube Full Albums:
    = Lofi:
      "Game Chops": "https://www.youtube.com/playlist?list=PLBsm_SagFMmdWnCnrNtLjA9kzfrRkto4i"

Let's break this down:

.. code-block:: yaml
  :lineno-start: 1

  __preset__:
    overrides:
      tv_show_directory: "/tv_shows"
      music_directory: "/music"


The first :ref:`__preset__ <config_reference/subscriptions_yaml:File Preset>` section is where we
can set modifications that apply to every subscription in this file.

This snippet specifically adds two :ref:`override <config_reference/plugins:Overrides>` variables,
which are used by the presets below.

.. note::
  It is tempting to put any override underneath ``overrides``. Keep in mind that this section
  is solely for variable defining. Other :ref:`plugins <config_reference/plugins:Plugins>` need to be
  set at the same indentation level as ``overrides``, not within it.


-------------------------------------

.. code-block:: yaml
  :lineno-start: 6

  # Can choose between:
  #  - Plex TV Show by Date:
  #  - Jellyfin TV Show by Date:
  #  - Kodi TV Show by Date:
  #

Lines 6-10 are comments that get ignored when parsing YAML since they are prefixed with ``#``.
It is good practice to leave informative comments in your config or subscription files to remind
yourself of various things.

-------------------------------------

.. code-block:: yaml
  :lineno-start: 11

  Jellyfin TV Show by Date:

On line 11, we set the key to ``Jellyfin TV Show by Date``. This is a
:ref:`prebuilt preset <prebuilt_presets/index:prebuilt presets>` that configures
subscriptions to look like TV shows in the Jellyfin media player (can be changed to
one of the presets outlined in the comment above). Setting it as a YAML key implies that all
subscriptions underneath it will *inherit* this preset.

This preset expects the variable ``tv_show_directory`` to be set, which we do above.

-------------------------------------

.. code-block:: yaml
  :lineno-start: 11

  Jellyfin TV Show by Date:
    = Documentaries:

Line 12 sets the key to ``= Documentaries``. When keys are prefixed with ``=``, it means we are
setting the genre. This value will get written to the respective metadata tags for both TV show
and music presets.

Behind the scenes, this sets the override variable ``subscription_indent_1``. Read more about
subscription syntax :ref:`here <config_reference/subscriptions_yaml:Subscriptions File>`.

-------------------------------------

.. code-block:: yaml
  :lineno-start: 11

  Jellyfin TV Show by Date:
    = Documentaries:
      "NOVA PBS": "https://www.youtube.com/@novapbs"

Line 13 is where we define our first subscription. We set the subscription name to ``NOVA PBS``,
and the subscription value to ``https://www.youtube.com/@novapbs``.

To see how presets ingest subscription definitions, refer to the
:ref:`preset references <config_reference/prebuilt_presets/tv_show:TV Show>`,
we can see that ``{subscription_name}`` is used to set the ``tv_show_name`` variable.

-------------------------------------

.. code-block:: yaml
  :lineno-start: 11

  Jellyfin TV Show by Date:
    = Documentaries:
      "NOVA PBS": "https://www.youtube.com/@novapbs"

    = Kids | = TV-Y:
      "Jake Trains": "https://www.youtube.com/@JakeTrains"

Line 15 underneath ``Jellyfin TV Show by Date``, but at the same level as ``= Documentaries``.
This means we'll inherit the TV show preset, but not the documentaries indent variable. We instead
set the indent variables to ``= Kids | = TV-Y``. This sets two indent variables. We can set
multiple presets and/or indent variables on the same key by using ``|`` as a separator.

Referring to the
:ref:`TV show preset reference <config_reference/prebuilt_presets/tv_show:TV Show>`, the first
two indent variables map to the TV show genre and TV show content rating.

The above info should be enough to understand the rest of the subscription file.