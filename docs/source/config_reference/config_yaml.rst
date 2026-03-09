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
``C:\\double\\bashslash\\paths`` in order to escape the backslash character. This is due
to it being a YAML escape character.

.. code-block:: yaml

  configuration:
    dl_aliases:
      mv: "--preset music_video"
      u: "--download.url"

    experimental:
      enable_update_with_info_json: True

    ffmpeg_path: "/usr/bin/ffmpeg"
    ffprobe_path: "/usr/bin/ffprobe"

    file_name_max_bytes: 255
    lock_directory: "/tmp"

    persist_logs:
      keep_successful_logs: True
      logs_directory: "/var/log/ytdl-sub-logs"

    umask: "022"
    working_directory: ".ytdl-sub-working-directory"

dl_aliases
----------
.. _dl_aliases:

Alias definitions to shorten :ref:`dl arguments <usage:Download Options>`. For example,

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
Experimental flags reside under the ``experimental`` key.

``enable_update_with_info_json``

Enables modifying subscription files using info.json files using the argument
``--update-with-info-json``. This feature is still being tested and has the ability to
destroy files. Ensure you have a full backup before usage. You have been warned!

ffmpeg_path
-----------
Path to ffmpeg executable. Defaults to ``/usr/bin/ffmpeg`` for Linux,
``./ffmpeg.exe`` in the same directory as ytdl-sub for Windows.

ffprobe_path
------------
Path to ffprobe executable. Defaults to ``/usr/bin/ffprobe`` for Linux,
``./ffprobe.exe`` in the same directory as ytdl-sub for Windows.

file_name_max_bytes
-------------------
Max file name size in bytes. Most OS's typically default to 255 bytes.

lock_directory
--------------
The directory to temporarily store file locks, which prevents multiple instances
of ``ytdl-sub`` from running. Note that file locks do not work on
network-mounted directories. Ensure that this directory resides on the host
machine. Defaults to ``/tmp``.

persist_logs
------------
By default, no logs are persisted. Specifying this key will enable persisted logs. The following
options are available.

``keep_successful_logs``

Defaults to ``True``. When this key is ``False``, only write log files for failed
subscriptions.

``logs_directory``

Required field. Write log files to this directory with names like
``YYYY-mm-dd-HHMMSS.subscription_name.(success|error).log``.

umask
-----
Umask in octal format to apply to every created file. Defaults to ``022``.

working_directory
-----------------
The directory to temporarily store downloaded files before moving them into their final
directory. Defaults to ``.ytdl-sub-working-directory``, created in the same directory
that ytdl-sub is invoked from.

Presets
=======
Custom presets are defined in this section. Refer to the
:ref:`Getting Started Guide<guides/getting_started/first_config:Basic Configuration>`
on how to configure.
