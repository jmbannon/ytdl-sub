Subscriptions
=============

Once you understand :ref:`how ytdl-sub works
<guides/getting_started/index:architecture>`, it's time to start writing your
:doc:`../../config_reference/subscription_yaml`.


Media library paths
-------------------

Everyone's media library may use different paths so ``ytdl-sub`` can't provide
defaults. Tell ``ytdl-sub`` where to put your media using :ref:`overrides
<guides/getting_started/index:presets and subscriptions accept overrides>`:

.. code-block:: yaml
  :caption: subscriptions.yaml
  :emphasize-lines: 3-

  __preset__:
    overrides:
      tv_show_directory: "/tv_shows"
      music_directory: "/music"
      music_video_directory: "/music_videos"

See the reference documentation for details about :ref:`the '__preset__:' special key
<config_reference/subscription_yaml:file preset>`.


Media library software and media types
--------------------------------------

Different media library software, such as `Jellyfin`_, `Kodi`_, Plex, or Emby, have
different requirements for where media files are placed, how those files are named, how
metadata is formatted, and more. Those software also have different requirements for
different types of media, such as shows/series, music, music videos, etc.. Use
:doc:`prebuilt presets <../../prebuilt_presets/index>` in :ref:`YAML keys
<guides/getting_started/index:subscriptions are grouped by indentation>` to tell
``ytdl-sub`` which media library software and media type to process downloaded files
for.

The actual subscription is defined in the lowest indentation level YAML keys. The
example below defines a subscription named ``NOVA PBS`` to archive downloads from the
entries in the ``https://www.youtube.com/@novapbs`` URL.

.. code-block:: yaml
  :caption: subscriptions.yaml
  :emphasize-lines: 1,4

  Jellyfin TV Show by Date:
    "NOVA PBS": "https://www.youtube.com/@novapbs"

  Bandcamp:
    "Emily Hopkins": "https://emilyharpist.bandcamp.com/"

.. _`Jellyfin`:
   https://jellyfin.org/
.. _`Kodi`:
   https://kodi.tv/


Which entries
-------------

The :doc:`helper presets <../../prebuilt_presets/helpers>` also provide support for
controlling which entries are downloaded and archived. These presets are intended to be
combined with the library software and media type presets.

Combine presets using :ref:`the '.. | ...' special character
<guides/getting_started/index:subscriptions are grouped by indentation>` in the YAML
keys:

.. code-block:: yaml
  :caption: subscriptions.yaml
  :emphasize-lines: 2,6

  # Only download entries whose upload date is within the past 2 months:
  Kodi TV Show by Date | Only Recent:
    "NOVA PBS": "https://www.youtube.com/@novapbs"

  # Only download 20 entries per run:
  Soundcloud Discography | Chunk Downloads:
    "UKNOWY": "https://soundcloud.com/uknowymunich"


What format, quality, or resolution
-----------------------------------

The :doc:`media quality presets <../../prebuilt_presets/media_quality>` provide support
for controlling which ``yt-dlp`` media "format" to download, such as ``1080p`` video
resolution or ``320k`` audio bitrate.

Users may also group and combine presets :ref:`using the YAML hierarchy
<guides/getting_started/index:subscriptions are grouped by indentation>`. Subscriptions
merge all the presets from their ancestor YAML keys. The hierarchy indentation depth may
be as deep as needed to group your subscriptions for easy maintenance:

.. code-block:: yaml
  :caption: subscriptions.yaml
  :emphasize-lines: 3,7,12

  Jellyfin TV Show by Date | Only Recent:
    # Download the highest resolution available:
    Max Video Quality:
      "NOVA PBS": "https://www.youtube.com/@novapbs"
      "National Geographic": "https://www.youtube.com/@NatGeo"
    # Download the highest resolution available that is 720p or less:
    Max 720p:
      "Cosmos - What If": "https://www.youtube.com/playlist?list=PLZdXRHYAVxTJno6oFF9nLGuwXNGYHmE8U"

  Soundcloud Discography | Chunk Downloads:
    # Only download audio using the Opus codec, not MP3 or other codecs:
    Max Opus Quality:
      "UKNOWY": "https://soundcloud.com/uknowymunich"


Genre and rating metadata
-------------------------

Presets may also support using arbitrary values from :ref:`YAML keys prefixed with '=
...' <guides/getting_started/index:subscriptions are grouped by indentation>`. The ``=
...`` prefix may be used at any indentation depth and may also be combined with presets
and other ``= ...`` values using the ``... | ...`` special character to best group your
subscriptions.

:ref:`By convention <config_reference/scripting/static_variables:subscription_indent_i>`
in the built-in library software and media type presets, the first ``= ...`` value
specifies the genre for all descendant subscriptions. For the ``TV Show ...`` presets,
the second ``= ...`` value specifies the rating for all descendant subscriptions:

.. code-block:: yaml
  :caption: subscriptions.yaml
  :emphasize-lines: 1,3

  = Kids:

    Jellyfin TV Show by Date | = TV-Y:
      "Jake Trains": "https://www.youtube.com/@JakeTrains"
      "Kids Toys Play": "https://www.youtube.com/@KidsToysPlayChannel"

    Soundcloud Discography:
      "Foo Kids Band": "https://soundcloud.com/foo-kids-band"


Override variables for one subscription
---------------------------------------

Most variable overrides aren't actually specific to just one subscription and should be
set in :doc:`your own custom presets <./first_config>`. But use :ref:`the override mode
'~...' prefix <config_reference/subscription_yaml:override mode>` when an override is
specific to only one subscription and will never be shared with another:

.. code-block:: yaml
  :caption: subscriptions.yaml
  :emphasize-lines: 2-

  Jellyfin TV Show by Date:
    "~NOVA PBS":
      url: "https://www.youtube.com/@novapbs"
      tv_show_directory: "/media/Unique/Series/Path"


Next Steps
----------

Once you've defined your subscriptions, it's time to :doc:`test the configuration and
try your first download <./first_download>`.
