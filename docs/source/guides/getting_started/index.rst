Getting Started
===============

Now that you've completed your install of ``ytdl-sub``, it's time to get started. This is a 3-step process:

- Create your configuration file (if the :doc:`/code_reference/prebuilt_presets` don't fit your needs)
- Create your subscription file
- Automate starting YTDL-Sub

Prerequisite Knowledge
----------------------

.. _navigate directories: https://en.wikipedia.org/wiki/Cd_(command)
.. _YAML syntax: https://yaml.org/spec/1.2.2/#chapter-2-language-overview


In order to use ``ytdl-sub`` in any of the forms listed in these docs, you will need some basic knowledge.

Be sure that you:
  ☑ Can `navigate directories`_ in a command line interface (or CLI)

  ☑ Have a basic understanding of `YAML syntax`_

If you plan on using the headless image of ``ytdl-sub``, you:
  ☑ Can use ``nano`` or ``vim`` to edit OR

  ☑ Can mount the config directory somewhere you can open it using gui text editors

Additional useful (but not required) knowledge:
  ☑ Understanding how :yt-dlp:`\ ` works


Quick Overview of ``ytdl-sub``
------------------------------

``ytdl-sub`` uses two types of YAML files:

- ``config.yaml`` defines ``presets``, which are the "definitions" of your media. ``presets`` "define" how you want your media downloaded, which formats, naming conventions to follow when saving them, etc. These ``presets`` can also inherit other ``presets``, so that you can easily modify an existing ``preset``.
- ``subscriptions.yaml`` defines ``subscriptions``, which specify the media we want to recurrently download, like YouTube channels and playlists, SoundCloud artists, or any :yt-dlp:`yt-dlp supported site <blob/master/supportedsites.md>`. ``subscriptions`` use ``presets`` to define how ``ytdl-sub`` should handle downloading, processing, and saving them.

When ``ytdl-sub`` is run, in its most basic form:

.. tab-set-code:: 

    .. code-block:: shell
        
        ytdl-sub sub

    .. code-block:: powershell

        ytdl-sub.exe sub

``ytdl-sub`` initially downloads all files to a defined ``working_directory``. This is a temporary storage spot for metadata and media files so that errors during processing- if they occur- don't affect your existing media library. Once all file processing is complete, your media files are moved to the ``output_directory``.

Ready to Start?
---------------

Now that you have installed ``ytdl-sub``, checked your skills, and gotten a bit of background on how ``ytdl-sub`` functions, read through the articles below to get started:

:doc:`Step 1: Initial Subscriptions <first_sub>`

:doc:`Step 2: Your First Download <first_download>`

:doc:`Step 3: Automating Downloads <automating_downloads>`

:doc:`Step 4: Initial Configuration <first_config>`

:doc:`Advanced Configuration <advanced_configuration>`

Other docs that may be of use:

:doc:`/code_reference/prebuilt_presets`

:doc:`examples`

.. toctree::
  :hidden:
  :caption: Getting Started Guide
  :maxdepth: 1

  first_config
  first_sub
  first_download
  automating_downloads
  advanced_configuration
  examples