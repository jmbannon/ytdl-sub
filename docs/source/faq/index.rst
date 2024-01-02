===
FAQ
===

Since ytdl-sub is relatively new to the public, there has not been many question asked yet. We will update this as more questions get asked.

.. contents:: Frequently Asked Questions
  :depth: 3

How do I...
-----------

...download age-restricted YouTube videos?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See `yt-dl's recommended way <https://github.com/ytdl-org/youtube-dl#how-do-i-pass-cookies-to-youtube-dl>`_ to download your YouTube cookie, then add it to your :ref:`ytdl options <config_reference/plugins:ytdl_options>` section of your config:

.. code-block:: yaml

  ytdl_options:
    cookiefile: "/path/to/cookies/file.txt"

...automate my downloads?
~~~~~~~~~~~~~~~~~~~~~~~~~

:doc:`This page </guides/getting_started/automating_downloads>` shows how to set up ``ytdl-sub`` to run automatically on various platforms.

There is a bug where...
-----------------------

...date_range is not downloading older videos after I changed the range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your preset most likely has ``break_on_existing`` set to True, which will stop downloading additional metadata/videos if the video exists in your download archive. Set the following in your config to skip downloading videos that exist instead of stopping altogether.

.. code-block:: yaml

  ytdl_options:
    break_on_existing: False

After you download your new date_range duration, re-enable ``break_on_existing`` to speed up successive downloads.

...it is downloading non-English title and description metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most likely the video has a non-English language set to its 'native' language. You can tell yt-dlp to explicitly download English metadata using.

.. code-block:: yaml

  ytdl_options:
    extractor_args:
      youtube:
        lang:
          - "en"

...Plex is not showing my TV shows correctly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set the following for your ytdl-sub library that has been added to Plex.

.. figure:: ../../images/plex_scanner_agent.png
  :alt: The Plex library editor, under the advanced settings, showing the required options for Plex to show the TV shows correctly.

**Scanner:** Plex Series Scanner

**Agent:** Personal Media shows

**Visibility:** Exclude from home screen and global search

**Episode sorting:** Library default

**YES** Enable video preview thumbnails