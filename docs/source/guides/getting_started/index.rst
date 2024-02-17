Getting Started
===============

Now that you've completed your install of ``ytdl-sub``, it's time to get started. This is a 3-step process:

- Create your configuration file (if the :doc:`/prebuilt_presets/index` don't fit your needs)
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

Overview
--------
``ytdl-sub`` uses two types of YAML files:

subscriptions.yaml
~~~~~~~~~~~~~~~~~~
Defines ``subscriptions``, which specify the media we want to recurrently download, like YouTube
channels and playlists, SoundCloud artists, or any
:yt-dlp:`yt-dlp supported site <blob/master/supportedsites.md>`. ``subscriptions`` use ``presets``
to define how ``ytdl-sub`` should handle downloading, processing, and saving them.

``ytdl-sub`` comes packaged with many
:ref:`prebuilt presets <prebuilt_presets/index:Prebuilt Presets>`
that will play nicely with well-known media players.

config.yaml
~~~~~~~~~~~
To customize ``ytdl-sub`` to beyond the prebuilt presets, you will need a ``config.yaml`` file. This
file is where custom ``presets`` can be defined to orchestrate ``ytdl-sub`` to your very specific needs.

Running ytdl-sub
~~~~~~~~~~~~~~~~
To invoke ``ytdl-sub`` to download subscriptions, use the following command:

.. tab-set-code:: 

    .. code-block:: shell
        
        ytdl-sub sub subscriptions.yaml

    .. code-block:: powershell

        ytdl-sub.exe sub subscriptions.yaml

``ytdl-sub`` initially downloads all files to a defined ``working_directory``. This is a temporary
storage spot for metadata and media files so that errors during processing- if they occur- don't
affect your existing media library. Once all file processing is complete, your media files are
moved to the ``output_directory``.

Ready to Start?
---------------

Now that you have installed ``ytdl-sub``, checked your skills, and gotten a bit of background on how ``ytdl-sub`` functions, read through the articles below to get started:

:doc:`Step 1: Initial Subscriptions <first_sub>`

:doc:`Step 2: Your First Download <first_download>`

:doc:`Step 3: Automating Downloads <automating_downloads>`

Want to go a step further?

If you want to use atypical paths or specific configuration options, check out :doc:`Basic Configuration <first_config>`

For tips on creating your own presets when the prebuilt presets aren't cutting it, check out :doc:`Advanced Configuration <advanced_configuration>`

Other docs that may be of use:

:doc:`/prebuilt_presets/index`

:doc:`examples`

.. toctree::
  :hidden:
  :caption: Getting Started Guide
  :maxdepth: 1

  first_sub
  first_download
  automating_downloads
  first_config
  advanced_configuration
  examples