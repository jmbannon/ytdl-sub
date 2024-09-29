Deprecation Notices
===================

Sep 2024
--------

regex plugin
~~~~~~~~~~~~
Regex plugin has been removed in favor of scripting. The function
:ref:`config_reference/scripting/scripting_functions:regex_capture_many`
has been created to replicate the plugin's behavior. See the following converted example:

.. code-block:: yaml
  :caption: regex plugin

    regex:
      from:
        title:
          match:
            - ".*? - (.*)"  # Captures 'Some - Song' from 'Emily Hopkins - Some - Song'
          capture_group_names:
            - "captured_track_title"
          capture_group_defaults:
            - "{title}"
    overrides:
      track_title: "{captured_track_title}"

.. code-block:: yaml
  :caption: scripting

    overrides:
      # Captures 'Some - Song' from 'Emily Hopkins - Some - Song'
      captured_track_title: >-
        {
          %regex_capture_many(
            title,
            [ ".*? - (.*)" ],
            [ title ]
          )
        }
      track_title: "{%array_at(captured_track_title, 1)}"

Oct 2023
--------

subscription preset and value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The use of ``__value__`` will go away in Dec 2023 in favor of the method found in
:ref:`config_reference/subscriptions_yaml:beautifying subscriptions`. ``__preset__`` will still be supported for the time being.

July 2023
---------

music_tags
~~~~~~~~~~

Music tags are getting simplified. ``tags`` will now reside directly under music_tags, and
``embed_thumbnail`` is getting moved to its own plugin (supports video files as well). Convert from:

.. code-block:: yaml

  my_example_preset:
    music_tags:
      embed_thumbnail: True
      tags:
        artist: "Elvis Presley"

To the following:

.. code-block:: yaml

  my_example_preset:
    embed_thumbnail: True
    music_tags:
      artist: "Elvis Presley"

The old format will be removed in October 2023.

video_tags
~~~~~~~~~~

Video tags are getting simplified as well. ``tags`` will now reside directly under video_tags.
Convert from:

.. code-block:: yaml

  my_example_preset:
    video_tags:
      tags:
        title: "Elvis Presley Documentary"

To the following:

.. code-block:: yaml

  my_example_preset:
    video_tags:
      title: "Elvis Presley Documentary"
