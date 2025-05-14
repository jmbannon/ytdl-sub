
Configuration File
==================
Something

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
TODO(jessebannon) fill out

``enable_update_with_info_json``

Enables modifying subscription files using info.json files using the argument
``--update-with-info-json``. This feature is still being tested and has the ability to
destroy files. Ensure you have a full backup before usage. You have been warned!

ffmpeg_path
-----------
Path to ffmpeg executable. Defaults to ``/usr/bin/ffmpeg`` for Linux, and
``ffmpeg.exe`` for Windows (in the same directory as ytdl-sub).

ffprobe_path
------------
Path to ffprobe executable. Defaults to ``/usr/bin/ffprobe`` for Linux, and
``ffprobe.exe`` for Windows (in the same directory as ytdl-sub).

file_name_max_bytes
-------------------
Max file name size in bytes. Most OS's typically default to 255 bytes.

lock_directory
--------------
The directory to temporarily store file locks, which prevents multiple instances
of ``ytdl-sub`` from running. Note that file locks do not work on network-mounted
directories. Ensure that this directory resides on the host machine. Defaults to ``/tmp``.

persist_logs
------------
TODO(jessebannon) fill out

``keep_successful_logs``

Optional. Whether to store logs when downloading is successful. Defaults to True.

``logs_directory``

Required. The directory to store the logs in.

umask
-----
Umask (octal format) to apply to every created file. Defaults to "022".

working_directory
-----------------
The directory to temporarily store downloaded files before moving them into their final
directory. Defaults to .ytdl-sub-working-directory
