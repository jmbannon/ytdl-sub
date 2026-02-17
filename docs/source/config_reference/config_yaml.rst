..
  WARNING: This RST file is generated from docstrings in:
    The respective function docstrings within ytdl_sub/config/config_validator.py
  In order to make a change to this file, edit the respective docstring
  and run `make docs`. This will automatically sync the Python RST-based
  docstrings into this file. If the docstrings and RST file are out of sync,
  it will fail TestDocGen tests in GitHub CI.

Configuration File
==================
ytdl-sub is configured using a ``config.yaml`` file.

The ``config.yaml`` is made up of two sections:

.. code-block:: yaml

  configuration:
  presets:


Note for Windows users, paths can be represented with ``C:/forward/slashes/like/linux``.
If you prefer to use a Windows backslash, note that it must have
``C:\double\bashslash\paths`` in order to escape the backslash character. This is due to
it being a YAML escape character.

dl_aliases
----------
.. _dl_aliases:

Alias definitions to shorten ``ytdl-sub dl`` arguments. For example,

.. code-block:: yaml

   configuration:
     dl_aliases:
       mv: "--preset music_video"
       u: "--download.url"

Simplifies

.. code-block:: bash

   ytdl-sub dl --preset "Jellyfin Music Videos" --download.url "youtube.com/watch?v=a1b2c3"

to

.. code-block:: bash

   ytdl-sub dl --mv --u "youtube.com/watch?v=a1b2c3"

experimental
------------
Experimental flags reside under the ``experimental`` key:

   .. code-block:: yaml

      configuration:
        experimental:
          enable_update_with_info_json: True

``enable_update_with_info_json``

Enables modifying subscription files using info.json files using the argument
``--update-with-info-json``. This feature is still being tested and has the ability to
destroy files. Ensure you have a full backup before usage. You have been warned!

ffmpeg_path
-----------
Path to ffmpeg executable. (default ``/usr/bin/ffmpeg`` for Linux,
``./ffmpeg.exe`` in the same directory as ytdl-sub for Windows)

ffprobe_path
------------
Path to ffprobe executable. (default ``/usr/bin/ffprobe`` for Linux,
``./ffprobe.exe`` in the same directory as ytdl-sub for Windows)

file_name_max_bytes
-------------------
Max file name size in bytes. Most OS's typically default to 255 bytes.

lock_directory
--------------
The directory to temporarily store file locks, which prevents multiple instances
of ``ytdl-sub`` from running. Note that file locks do not work on
network-mounted directories. Ensure that this directory resides on the host
machine. (default ``/tmp``)

persist_logs
------------
TODO(jessebannon) fill out

``keep_successful_logs``

If the ``persist_logs:`` key is in the configuration, then ``ytdl-sub`` *always*
writes log files for the subscription both for successful downloads and when it
encounters an error while downloading. When this key is ``False``, only write
log files for errors. (default ``True``)

``logs_directory``

Write log files to this directory with names like
``YYYY-mm-dd-HHMMSS.subscription_name.(success|error).log``. (required)

umask
-----
Umask in octal format to apply to every created file. (default ``022``)

working_directory
-----------------
The directory to temporarily store downloaded files before moving them into their final
directory. (default ``./.ytdl-sub-working-directory``)
