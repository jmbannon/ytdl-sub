Install
=======
``ytdl-sub`` can be installed on the following platforms.

.. contents::
    :depth: 2

All installations require a 64-bit CPU. 32-bit is not supported.

Docker Compose
--------------
The ytdl-sub docker image uses
`Linux Server's <https://www.linuxserver.io/>`_
`base alpine image <https://github.com/linuxserver/docker-baseimage-alpine/>`_
It looks, feels, and operates like other LinuxServer images. This is the
recommended way to use ytdl-sub.

The docker image is intended to be used as a console. For automating
``subscriptions.yaml`` downloads to pull new media, see
`this guide <https://github.com/jmbannon/ytdl-sub/wiki/7.-Automate-Downloading-New-Content-Using-Your-Configs/>`_
on how set up a cron job in the docker container.

.. code-block:: yaml

   services:
     ytdl-sub:
       image: ghcr.io/jmbannon/ytdl-sub:latest
       container_name: ytdl-sub
       environment:
         - PUID=1000
         - PGID=1000
         - TZ=America/Los_Angeles
         - DOCKER_MODS=linuxserver/mods:universal-cron
       volumes:
         - <path/to/ytdl-sub/config>:/config
         - <path/to/tv_shows>:/tv_shows  # optional
         - <path/to/movies>:/movies  # optional
         - <path/to/music_videos>:/music_videos  # optional
         - <path/to/music>:/music  # optional
       restart: unless-stopped

Nvidia GPU Passthrough
^^^^^^^^^^^^^^^^^^^^^^
For GPU passthrough, you must use the ``ytdl-sub`` Ubuntu version with the following additions:

.. code-block:: yaml

   services:
     ytdl-sub:
       image: ghcr.io/jmbannon/ytdl-sub:ubuntu-latest
       container_name: ytdl-sub
       environment:
         - PUID=1000
         - PGID=1000
         - TZ=America/Los_Angeles
         - DOCKER_MODS=linuxserver/mods:universal-cron
         - NVIDIA_DRIVER_CAPABILITIES=all  # Nvidia ENV args
         - NVIDIA_VISIBLE_DEVICES=all
       volumes:
         - <path/to/ytdl-sub/config>:/config
         - <path/to/tv_shows>:/tv_shows  # optional
         - <path/to/movies>:/movies  # optional
         - <path/to/music_videos>:/music_videos  # optional
         - <path/to/music>:/music  # optional
       deploy:
         resources:
           reservations:
             devices:
               - capabilities: [gpu]  # GPU passthrough
       restart: unless-stopped

CPU Passthrough
^^^^^^^^^^^^^^^^^^^^^^
For CPU passthrough, you must use the ``ytdl-sub`` Ubuntu version with the following additions:

.. code-block:: yaml

   services:
     ytdl-sub:
       image: ghcr.io/jmbannon/ytdl-sub:ubuntu-latest
       container_name: ytdl-sub
       environment:
         - PUID=1000
         - PGID=1000
         - TZ=America/Los_Angeles
         - DOCKER_MODS=linuxserver/mods:universal-cron
       volumes:
         - <path/to/ytdl-sub/config>:/config
         - <path/to/tv_shows>:/tv_shows  # optional
         - <path/to/movies>:/movies  # optional
         - <path/to/music_videos>:/music_videos  # optional
         - <path/to/music>:/music  # optional
       devices:
         - /dev/dri:/dev/dri  # CPU passthrough
       restart: unless-stopped

Docker
--------------
.. code-block:: bash

   docker run -d \
       --name=ytdl-sub \
       -e PUID=1000 \
       -e PGID=1000 \
       -e TZ=America/Los_Angeles \
       -e DOCKER_MODS=linuxserver/mods:universal-cron \
       -v <path/to/ytdl-sub/config>:/config \
       -v <OPTIONAL/path/to/tv_shows>:/tv_shows \
       -v <OPTIONAL/path/to/movies>:/movies \
       -v <OPTIONAL/path/to/music_videos>:/music_videos \
       -v <OPTIONAL/path/to/music>:/music \
       --restart unless-stopped \
       ghcr.io/jmbannon/ytdl-sub:latest

Windows
--------------
From powershell, run:

.. code-block:: powershell

   # Download ffmpeg/ffprobe dependencies from yt-dlp
   curl.exe -L -o ffmpeg.zip https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip
   tar -xf ffmpeg.zip
   move "ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" "ffmpeg.exe"
   move "ffmpeg-master-latest-win64-gpl\bin\ffprobe.exe" "ffprobe.exe"

   # Download ytdl-sub
   curl.exe -L -o ytdl-sub.exe https://github.com/jmbannon/ytdl-sub/releases/latest/download/ytdl-sub.exe
   ytdl-sub.exe -h

Linux
--------------
Requires ffmpeg as a dependency. Can typically be installed with any Linux package manager.

.. code-block:: bash

   curl -L -o ytdl-sub https://github.com/jmbannon/ytdl-sub/releases/latest/download/ytdl-sub
   chmod +x ytdl-sub
   ytdl-sub -h

You can also install using yt-dlp's ffmpeg builds. This ensures your ffmpeg is up to date:

.. code-block:: bash

   curl -L -o ffmpeg.tar.gz https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
   tar -xf ffmpeg.tar.gz
   chmod +x ffmpeg-master-latest-linux64-gpl/bin/ffmpeg
   chmod +x ffmpeg-master-latest-linux64-gpl/bin/ffprobe

   # May need sudo / root permissions to perform
   mv ffmpeg-master-latest-linux64-gpl/bin/ffmpeg /usr/bin/ffmpeg
   mv ffmpeg-master-latest-linux64-gpl/bin/ffprobe /usr/bin/ffprobe

Linux ARM
--------------
Requires ffmpeg as a dependency. Can typically be installed with any Linux package manager.

.. code-block:: bash

   curl -L -o ytdl-sub https://github.com/jmbannon/ytdl-sub/releases/latest/download/ytdl-sub_aarch64
   chmod +x ytdl-sub
   ytdl-sub -h

You can also install using yt-dlp's ffmpeg builds. This ensures your ffmpeg is up to date:

.. code-block:: bash

   curl -L -o ffmpeg.tar.gz https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linuxarm64-gpl.tar.xz
   tar -xf ffmpeg.tar.gz
   chmod +x ffmpeg-master-latest-linuxarm64-gpl/bin/ffmpeg
   chmod +x ffmpeg-master-latest-linuxarm64-gpl/bin/ffprobe

   # May need sudo / root permissions to perform
   mv ffmpeg-master-latest-linuxarm64-gpl/bin/ffmpeg /usr/bin/ffmpeg
   mv ffmpeg-master-latest-linuxarm64-gpl/bin/ffprobe /usr/bin/ffprobe


PIP
--------------
You can install our
`PyPI package <https://pypi.org/project/ytdl-sub/>`_.
Both ffmpeg and Python 3.10 or greater are required.

.. code-block:: bash

   python3 -m pip install -U ytdl-sub

Local Install
--------------
With a Python 3.10 virtual environment, you can clone and install the repo using

.. code-block:: bash

   git clone https://github.com/jmbannon/ytdl-sub.git
   cd ytdl-sub

   pip install -e .

Local Docker Build
-------------------
Run ``make docker`` in the root directory of this repo to build the image. This
will build the python wheel and install it in the Dockerfile.

