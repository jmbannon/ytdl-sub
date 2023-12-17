Deprecation Notices
===================

Oct 2023
--------

subscription preset and value
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The use of ``__value__`` will go away in Dec 2023 in favor of the method found in
:ref:`beautifying subscriptions`. ``__preset__`` will still be supported for the time being.

July 2023
---------

music_tags
^^^^^^^^^^

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
^^^^^^^^^^

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
