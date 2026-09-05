===
FAQ
===

Since ytdl-sub is relatively new to the public, there has not been many question asked
yet. We will update this as more questions get asked.

.. contents:: Frequently Asked Questions
  :depth: 3


How do I...
-----------

...remove the date in the video title?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :ref:`config_reference/prebuilt_presets/tv_show:TV Show` presets by default include
the upload date in the ``episode_title`` override variable. This variable is used to set
the title in things like the video metadata, NFO file, etc, which is subsequently read
by media players. This can be overwritten as you see fit by redefining it:

.. code-block:: yaml

   overrides:
     episode_title: "{title}"  # Only sets the video title

...download age-restricted YouTube videos?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See `yt-dl's recommended way
<https://github.com/ytdl-org/youtube-dl#how-do-i-pass-cookies-to-youtube-dl>`_ to
download your YouTube cookie, then add it to your :ref:`ytdl options
<config_reference/plugins:ytdl_options>` section of your config:

.. code-block:: yaml

  ytdl_options:
    cookiefile: "/path/to/cookies/file.txt"

...automate my downloads?
~~~~~~~~~~~~~~~~~~~~~~~~~

:doc:`This page </guides/getting_started/automating_downloads>` shows how to set up
``ytdl-sub`` to run automatically on various platforms.

...download large channels?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

See the prebuilt preset :doc:`chunk_initial_download </prebuilt_presets/helpers>`.

...filter to include or exclude based on certain keywords?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See the prebuilt preset :doc:`Filter Keywords </prebuilt_presets/helpers>`.

...prevent creation of NFO file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creation of NFO files is done by the NFO tags plugin. It, as any other plugin, can be
disabled:

.. code-block:: yaml

  nfo_tags:
    enabled: False

...prevent download of images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :ref:`config_reference/prebuilt_presets/tv_show:TV Show` presets by default
downloads images corresponding to show and each episode.  This can be prevented by
overriding following variables:

.. code-block:: yaml

  overrides:
    tv_show_fanart_file_name: ""  # to stop creation of fanart.jpg in subscription
    tv_show_poster_file_name: ""  # to stop creation of poster.jpg in subscription
    thumbnail_name: ""            # to stop creation of episode thumbnails

...use only part of the media's title
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ytdl-sub offers a range of functions that can be used to parse a subset of a title for
use in your media player. Consider the example:

* I want to remove "NOVA PBS - " from the title ``NOVA PBS - Hidden Cities All Around
  Us``.

There are several solutions using ytdl-sub's scripting capabilities to override
``episode_title`` by manipulating the original media's ``title``.

.. code-block:: yaml
   :caption: Replace exclusion with empty string

   "~Nova PBS":
     url: "https://www.youtube.com/@novapbs"
     episode_title: >-
       {
         %replace( title, "NOVA PBS - ", "" )
       }

.. code-block:: yaml
   :caption: Split once using delimiter, grab last value in the split array.

   "~Nova PBS":
     url: "https://www.youtube.com/@novapbs"
     episode_title: >-
       {
         %array_at( %split(title, " - ", 1), -1 )
       }

.. code-block:: yaml
   :caption:
      Regex capture. Supports multiple capture strings and default values if captures
      are unsuccessful.

   "~Nova PBS":
     url: "https://www.youtube.com/@novapbs"
     captured_episode_title: >-
       {
         %regex_capture_many(
           title,
           [ "NOVA PBS - (.*)" ],
           [ title ]
         )
       }
     episode_title: >-
        { %array_at( captured_episode_title, 1 ) }

There is no single solution to this problem - it will vary case-by-case. See our full
suite of :ref:`scripting functions
<config_reference/scripting/scripting_functions:Scripting Functions>` to create your own
clever scraping mechanisms.

...force ytdl-sub to re-download a file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes users may wish to replace a file already in the archive, for example, if the
current file is a lower resolution than desired, missing subtitles, corrupt, etc..

``ytdl-sub`` decides what files have already been downloaded by entries in :ref:`the
download archive file <config_reference/plugins:output_options>`,
``./.ytdl-sub-...-download-archive.json``, at the top of the subscription/series/show
:ref:`output directory <config_reference/plugins:output_options>` in the appropriate
``overrides: / ..._directory:`` library path, *and* the presence of the corresponding
downloaded files under the same path. To force ``ytdl-sub`` to re-download an entry both
need to be removed:

- Move aside the downloaded files:

  Rename or move the downloaded files, including the associated files with the same
  base/stem name, such as ``./*.nfo``, ``./*.info-json``, etc... Ytdl-sub checks both
  the file system and the download archive file, so we must remove the item in question
  from both places for it to be downloaded again.

- Ensure ``ytdl-sub`` is not running and won't run, such as by cron:

  ``ytdl-sub`` loads the ``./.ytdl-sub-...-download-archive.json`` file early, keeps it
  in memory, and writes it back out late. If it's running or starts running while you're
  modifying that file, then your changes will be overwritten when it exits.

- Remove the ``./.ytdl-sub-...-download-archive.json`` JSON array item:

  Search for the stem name, the basename without any extension or suffix, common to all
  the downloaded files in this file and delete that whole entry, from the YouTube ID
  string to the closing curly braces. Be ware of JSON traling commas.

- Run ``$ ytdl-sub sub`` again with the appropriate CLI plugin options:

  In normal operation, :ref:`yt-dlp minimizes requests and the files considered for
  download <guides/getting_started/index:minimize the work to only what's
  necessary>`. To re-download, those options must be disabled or modified. Disable
  :ref:`the 'break_on_existing' option <config_reference/plugins:ytdl_options>`, set
  :ref:`the 'date_range:' plugin <config_reference/plugins:date_range>`, and :ref:`limit
  the subscriptions <guides/getting_started/downloading:preview>` to
  download only the files that you've renamed in the steps above.

  Setting 'break_on_existing' to false will force a new scrape, but will not re-download
  files that exist in the archive or on disk.

  Set the appropriate dates, :ref:`including a sufficient margin
  <config_reference/plugins:date_range>`, and subscription name to include only the
  files you've renamed, and re-run. For example, if you've renamed all the files from
  2024 in the ``NOVA PBS`` subscription:

    .. code-block:: shell

       ytdl-sub --match="NOVA PBS" sub -o "\
       --ytdl_options.break_on_existing False \
       --date_range.after 20240101 \
       --date_range.before 20250101 \
       "

...download a file missing from the archive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The root causes are unknown, but sometimes even after successful, complete runs, some
files will be missing from the archive. To attempt to download those missing files,
use `the same CLI options as re-downloading a file`_

.. _`the same CLI options as re-downloading a file`:
   `...force ytdl-sub to re-download a file`_

The key option is 'break_on_existing'. Try setting 'break_on_existing' to 'false' in
your subscription file. This will force a full re-scrape, but will not re-download
existing files.

...get support?
~~~~~~~~~~~~~~~

See :doc:`the debugging documentation <../debugging>`.

...reach out to contribute?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you would like to contribute, we're happy to accept any help, including from
non-coders! To find out how you can help this project, you can:

- `Join our Discord <https://discord.gg/v8j9RAHb4k>`_ and leave a comment in
  #development with where you think you can assist or what skills you would like to
  contribute.

- If you just want to fix one thing, you're welcome to :ytdl-sub-gh:`submit a pull
  request <compare>` with information on what issue you're resolving and it will be
  reviewed as soon as possible.


There is a bug where...
-----------------------

...ytdl-sub is not downloading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

...ytdl-sub is downloading at 360p or other lower quality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

...ytdl-sub downloads 2-4 videos and then fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are often just limits imposed by the external services that are not bugs. There
may be little that can be done about them, but see :ref:`the '_throttle_protection'
preset <prebuilt_presets/helpers:_throttle_protection>` for more information.

...date_range is not downloading older videos after I changed the range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your preset most likely has ``break_on_existing`` set to True, which will stop
downloading additional metadata/videos if the video exists in your download archive. Set
the following in your config to skip downloading videos that exist instead of stopping
altogether.

.. code-block:: yaml

  ytdl_options:
    break_on_existing: False

After you download your new date_range duration, re-enable ``break_on_existing`` to
speed up successive downloads.

...it is downloading non-English title and description metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most likely the video has a non-English language set to its 'native' language. You can
tell yt-dlp to explicitly download English metadata using.

.. code-block:: yaml

  ytdl_options:
    extractor_args:
      youtube:
        lang:
          - "en"

...Plex is not showing my TV shows correctly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Set the following for your ytdl-sub library that has been added to Plex.

.. figure:: ../../images/plex_scanner_agent.png
  :alt:
     The Plex library editor, under the advanced settings, showing the required options
     for Plex to show the TV shows correctly.

- **Scanner:** Plex Series Scanner
- **Agent:** Personal Media shows
- **Visibility:** Exclude from home screen and global search
- **Episode sorting:** Library default
- **YES** Enable video preview thumbnails

2. Under **Settings** > **Agents**, confirm Plex Personal Media Shows/Movies scanner has
   **Local Media Assets** enabled.

.. figure:: ../../images/plex_agent_sources.png
  :alt:
     The Plex Agents settings page has Local Media Assets enabled for Personal Media
     Shows and Movies tabs.

...ytdl-sub errors when downloading a 360p video with resolution assert
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:ref:`See how to either ignore this specific video or disable resolution assertion entirely here. <resolution assert handling>`
