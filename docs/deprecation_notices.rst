Deprecation Notices
===================

July 2023
---------

embed_thumbnail
^^^^^^^^^^^^^^^

Embedding thumbnails has its own dedicated plugin now, which supports both audio and video files.
It will be removed from ``music_tags`` in October 2023. Convert from:

.. code-block:: yaml

   my_example_preset:
     music_tags:
       embed_thumbnail: True

To the following:

.. code-block:: yaml

   my_example_preset:
     embed_thumbnail: True

