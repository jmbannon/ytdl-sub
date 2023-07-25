Deprecation Notices
===================

July 2023
---------

music_tags
^^^^^^^^^^

Music tags is getting simplified. ``tags`` will now reside directly under music_tags, and
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
