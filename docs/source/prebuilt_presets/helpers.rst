


==============
Helper Presets
==============

.. hint::

   See how to apply helper presets :doc:`here </prebuilt_presets/index>`


Only Recent
-----------

To only download a recent number of videos, apply the ``Only Recent`` preset. Once a
video's upload date is outside of the range, or you hit max files, older videos will be
deleted automatically.

.. code-block:: yaml

   __preset__:
     overrides:
       # Set to a non-zero value to only keep this many files at once per sub
       only_recent_max_files: 0
       only_recent_date_range: "7days"

   Plex TV Show by Date | Only Recent:

     = Documentaries:
       "NOVA PBS": "https://www.youtube.com/@novapbs"

To prevent deletion of files, use the preset ``Only Recent Archive`` instead.


Filter Keywords
---------------

``Filter Keywords`` can include or exclude media with any of the listed keywords. Both
keywords and title/description are lower-cased before filtering.

Default behavior for Keyword evaluation is ANY, meaning the filter will succeed if any
of the keywords are present. This can be set to ANY or ALL using the respective
``_eval`` variable.

Supports the following override variables:

* ``title_include_keywords``, ``title_include_eval``
* ``title_exclude_keywords``, ``title_exclude_eval``
* ``description_include_keywords``, ``title_exclude_eval``
* ``description_exclude_keywords``, ``title_exclude_eval``

.. tip::

   Use the `~` tilda subscription mode to set a subscription's list override variables.
   Tilda mode allows override variables to be set directly underneath it.

   .. code-block:: yaml

      Plex TV Show by Date | Filter Keywords:

        = Documentaries:
          "~NOVA PBS":
            url: "https://www.youtube.com/@novapbs"
            title_exclude_keywords:
              - "preview"
              - "trailer"

          "~To Catch a Smuggler":
            url: "https://www.youtube.com/@NatGeo"
            title_include_keywords:
              - "To Catch a Smuggler"

        = Sports:
          "~Maple Leafs Highlights":
            url: "https://www.youtube.com/@NHL"
            title_include_eval: "ALL"
            title_include_keywords:
              - "maple leafs"
              - "highlights"


Filter Duration
---------------

``Filter Duration`` can include or exclude media based on its duration.

Supports the following override variables:

* ``filter_duration_min_s``
* ``filter_duration_max_s``

.. tip::

   Use the `~` tilda subscription mode to set a subscription's list override variables.
   Tilda mode allows override variables to be set directly underneath it.

   .. code-block:: yaml

      Plex TV Show by Date | Filter Duration:

        = Documentaries:
          "~NOVA PBS":
            url: "https://www.youtube.com/@novapbs"
            filter_duration_min_s: 120  # Only download videos at least 2m long

        = Sports:
          "~Maple Leafs Highlights":
            url: "https://www.youtube.com/@NHL"
            filter_duration_max_s: 180  # Only get highlight videos less than 3m long


Chunk Downloads
---------------

If you are archiving a large channel, ``ytdl-sub`` will try pulling each video's
metadata from newest to oldest before starting any downloads. It is a long process and
not ideal. A better method is to chunk the process by using the following preset:

``Chunk Downloads``

It will download videos starting from the oldest one, and only download 20 at a time by
default. You can change this number by setting the override variable
``chunk_max_downloads``.

.. code-block:: yaml

   __preset__:
     overrides:
       chunk_max_downloads: 20

   Plex TV Show by Date:

     # Chunk these ones
     = Documentaries | Chunk Downloads:
       "NOVA PBS": "https://www.youtube.com/@novapbs"
       "National Geographic": "https://www.youtube.com/@NatGeo"

     # But not these ones
     = Documentaries:
       "Cosmos - What If": "https://www.youtube.com/playlist?list=PLZdXRHYAVxTJno6oFF9nLGuwXNGYHmE8U"

Once the entire channel is downloaded, remove the usage of this preset. It will then
pull metadata from newest to oldest again, and stop once it reaches a video that has
already been downloaded.


_throttle_protection
--------------------

.. note::

   This preset is already a base preset of those higher-level presets that require it,
   so users seldom need to use it directly, for example, unless they're writing presets
   from scratch.

This preset is primarily a sensible default configuration of :ref:`the
'throttle_protection' plugin <config_reference/plugins:throttle_protection>` along with
an override to disable the plugin:

.. code-block:: yaml

   overrides:
     # Disable throttle protection:
     enable_throttle_protection: false

In addition to throttling by denying download requests, some services also throttle
downloads by only allowing downloads of the lowest resolution quality. At the time of
writing, only YouTube does this by allowing only 360p downloads when throttled. To work
around this kind of throttling, this preset includes :ref:`an assertion
<config_reference/scripting/scripting_functions:error functions>` that will stop
downloading when ``ytdl-sub`` downloads a video at 360p or lower. It supports the
following overrides:

.. code-block:: yaml

   overrides:
     # Disable resolution quality throttle protection:
     enable_resolution_assert: false
     # Change the resolution below which to assume downloading is throttled:
     resolution_assert_height_gte: 720

.. _resolution assert handling:

Handling Low Quality Videos
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A side effect from throttle protection's resolution assert is, if the only resolution available is 360p or lower, it will
error. You can either disable resolution assert entirely (see above), or ignore specific titles in the subscription
using the ``resolution_assert_ignore_titles`` variable. Add a subset of the title (case-sensitive) as a list entry
to your subscription, like so:

.. code-block:: yaml

   # use tilda mode to set override variables to the subscription
   "~My Subscription":
     url: "https://youtube.com/@channel"
     resolution_assert_ignore_titles:
       - "This 360p Video Title"

_url
----

All prebuilt presets share the same internal ``_multi_url`` preset which comes equipped with
a few available customizations.

Sibling Metadata
~~~~~~~~~~~~~~~~

*Sibling* refers to any entry within the same *playlist*. For channel downloads, this would
imply **every** video that gets downloaded since yt-dlp treats the channel as the *playlist*.

Setting the variable ``include_sibling_metadata`` will include all sibling metadata within
each individual entry's metadata. This is used specifically for music presets. When downloading
a playlist as an album for example, it will take the max year amongst all the other sibling's metadata
to have a consistent album year that can be used in file or directory naming.

Webpage URL
~~~~~~~~~~~

``ytdl-sub`` performs downloads in two stages.

1. Metadata scrape from the original URL
2. Individual entry downloads

For step 2, ``ytdl-sub`` will use the ``webpage_url`` variable by default for the input URL to yt-dlp.
This can be modified in case it's not working as expected by using the variable ``modified_webpage_url``.

Example:

.. code-block:: yaml
  :caption:
     Removes yt-dlp smuggle data from the URL

   overrides:
     modified_webpage_url: >-
       { %regex_sub("#__youtubedl_smuggle=.*", "", webpage_url) }