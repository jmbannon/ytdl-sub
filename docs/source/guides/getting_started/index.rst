Getting Started
===============

Prerequisite Knowledge
----------------------

As a lower level tool with no GUI, ``ytdl-sub`` requires some technical knowledge. You
must be able to:

- do `basic CLI shell navigation`_
- read and write `YAML text files`_

If you plan on using a :ref:`Docker headless image variant
<guides/install/docker:headless image>` of ``ytdl-sub``, you can:

- use ``$ nano /config/...`` to edit configuration files inside the container
- or bind mount ``/config/`` as a Docker volume and use the editor of your choice from
  the host

.. _`basic CLI shell navigation`:
   https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Command_line
.. _`YAML text files`: http://thomasloven.com/blog/2018/08/YAML-For-Nonprogrammers/


Terminology
-----------

Must-know terminology:

- ``subscription``: URL(s) that you want to download with specific metadata requirements.
- ``preset``: A media profile comprised of YAML configuration that can specify anything from metadata layout, media quality, or any feature of ytdl-sub, to apply to subscriptions. A preset can inherit other presets.
- ``prebuilt preset``: Presets that are included in ytdl-sub. These do most of the work defining plugins, overrides, etc in order to make downloads ready for player consumption.
- ``override``: Verb describing the act of overriding something in a preset. For example, the TV Show presets practically expect you to *override* the URL variable to tell ytdl-sub where to download from.
- ``override variables``: User-defined variables that are intended to *override* something.
- ``subscription file``: The file to specify all of your subscriptions and some override variables.

Intermediate terminology:

- ``plugin``: Modular logic to apply to a subscription. To use a plugin, it must be defined in a preset.
- ``config file``: An optional file where you can define custom presets and other advanced configuration.
- ``yt-dlp``: The underlying application that handles downloading for ytdl-sub.

Advanced terminology:

- ``entry variables``: Variables that derive from a downloaded yt-dlp entry (media).
- ``static variables``: Variables that do not have a dependency to entry variables.
- ``scripting``: Syntax that allows the use of entry variables, static variables, and functions in override variables.

Ready to Start?
---------------
Now that you've completed your install of ``ytdl-sub``, it's time to get started.
It is recommended to go through the below sections in order to fully grasp ytdl-sub.

.. toctree::
  :maxdepth: 2

  first_sub
  first_download
  automating_downloads
  first_config
