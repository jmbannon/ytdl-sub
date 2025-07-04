==============
Helper Presets
==============

.. hint::

   See how to apply helper presets :doc:`here </prebuilt_presets/index>`

Only Recent
-----------

To only download a recent number of videos, apply the ``Only Recent`` preset. Once a video's
upload date is outside of the range, or you hit max files, older videos will be deleted automatically.

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

``Filter Keywords`` can include or exclude media with any of the listed keywords. Both keywords and title/description are lower-cased before filtering.

Default behavior for Keyword evaluation is ANY, meaning the filter will succeed if any of the keywords are present. This can be set to ANY or ALL using the respective ``_eval`` variable.

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

      Plex TV Show by Date | Filter Keywords:

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

If you are archiving a large channel, ``ytdl-sub`` will try pulling each video's metadata from newest to oldest before
starting any downloads. It is a long process and not ideal. A better method is to chunk the process by using the
following preset:

``Chunk Downloads``

It will download videos starting from the oldest one, and only download 20 at a time by default. You can
change this number by setting the override variable ``chunk_max_downloads``.

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

Once the entire channel is downloaded, remove the usage of this preset. It will then pull metadata from newest to
oldest again, and stop once it reaches a video that has already been downloaded.