FAQ
===

Since ytdl-sub is relatively new to the public, there has not been many question asked yet. We will update this as
more questions get asked.

.. contents:: Frequently Asked Questions
  :depth: 3

How do I...
-----------

...download age-restricted YouTube videos?
''''''''''''''''''''''''''''''''''''''''''
See
`ytdls recommended way <https://github.com/ytdl-org/youtube-dl#how-do-i-pass-cookies-to-youtube-dl>`_
to download your YouTube cookie, then add it to your
`ytdl options <https://ytdl-sub.readthedocs.io/en/latest/config.html#ytdl-options>`_ section of your config:

.. code-block:: yaml

   ytdl_options:
     cookiefile: "/path/to/cookies/file.txt"

...automate my downloads?
'''''''''''''''''''''''''
`This part of the wiki <https://github.com/jmbannon/ytdl-sub/wiki/7.-Automate-Downloading-New-Content-Using-Your-Configs>`_ shows how to set up ``ytdl-sub`` to run in a cron job within Docker.

There is a bug where...
-----------------------

...date_range is not downloading older videos after I changed the range
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Your preset most likely has ``break_on_existing`` set to True, which will stop downloading additional metadata/videos if the video exists in your download archive. Set the following in your config to skip downloading videos that exist instead of stopping altogether.

.. code-block:: yaml

   ytdl_options:
     break_on_existing: False

After your download your new date_range duration, re-enable ``break_on_existing`` to speed up successive downloads.

...it is downloading non-English title and description metadata
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Most likely the video has a non-English language set to its 'native' language. You can tell yt-dlp to explicitly download English metadata using

.. code-block:: yaml

   ytdl_options:
     extractor_args:
       youtube:
         lang:
           - "en"

...Plex is not showing my TV shows correctly
''''''''''''''''''''''''''''''''''''''''''''
Set the following
`Scanner and Agent <https://i.imgur.com/zdZhCLZ.png>`_
for your library.