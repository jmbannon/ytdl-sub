Getting Started
===============

The goal of this app is automate the downloading and metadata creation of audio and video files, then place the files
in a directory that gets read by your media player/server. Everyone stores and watches their media differently, so
we strive for comprehensive and simplistic customization to fit all self-hosting needs.

Audio metadata is just a matter of adding tags to the audio file. The backend plugin we use supports practically every
common audio file type, so there should (hopefully) be no issues getting audio recognized by your media player.

Video metadata on the other hand, is currently geared toward generating Kodi/Jellyfin/Emby NFO files. Plex uses metadata
written within MP4 containers - we do not support that currently, but could be added as a plugin in the future.

Usage Ideas
-----------
Below is a list ways you can use ytdl-sub to download and consume different kinds of media in the representation you
prefer.

* Download a Youtube channel
    * Store the channel as its own TV Show
        * Use the channel's avatar as the TV Show poster, banner as the fanart
        * Format the season and episodes as ``Season YYYY/sYYYY.eMMDD - Video Title.mp4`` to easily navigate videos by upload date
    * Store the channel as a single season under a TV Show shared with other channels
    * Only download audio, store it as a Podcast
    * Only keep video/audio uploaded in the last `N` days
        * Great for news or podcast based channels

* Download a Youtube playlist
    * Download an artist's music videos playlist, store each video as a Kodi/Jellyfin/Emby Music Video
    * Only download the audio, store the playlist as an album

* Manually download a single Youtube video
    * Store it as a Movie
    * Download a one-hit wonder and store it as a Kodi/Jellyfin/Emby Music Video

* Download a soundcloud artist's discography
    * Add tags and album cover images so it shows up nicely in your music player

If you want to jump the gun to see how ytdl-sub can be configured to do these things, head over to the
:doc:`examples <examples>`.

Install
-------

The ytdl-sub docker image uses
`LinuxServer's <https://www.linuxserver.io/>`_
`base alpine image <https://github.com/linuxserver/docker-baseimage-alpine>`_.
It looks, feels, and operates like other LinuxServer images. This is the
recommended way to use ytdl-sub.

Docker Compose
______________

.. code-block:: yaml

   version: "2.1"
   services:
     ytdl-sub:
       image: ghcr.io/jmbannon/ytdl-sub:latest
       container_name: ytdl-sub
       environment:
         - PUID=1000
         - PGID=1000
         - TZ=America/Los_Angeles
       volumes:
         - <path/to/ytdl-sub/config>:/config
         - <path/to/tv_shows>:/tv_shows # optional
         - <path/to/movies>:/movies # optional
         - <path/to/music_videos>:/music_videos # optional
         - <path/to/music>:/music # optional
       restart: unless-stopped

Docker CLI
__________

.. code-block:: bash

   docker run -d \
     --name=ytdl-sub \
     -e PUID=1000 \
     -e PGID=1000 \
     -e TZ=America/Los_Angeles \
     -v <path/to/ytdl-sub/config>:/config \
     -v <OPTIONAL/path/to/tv_shows>:/tv_shows \
     -v <OPTIONAL/path/to/movies>:/movies \
     -v <OPTIONAL/path/to/music_videos>:/music_videos \
     -v <OPTIONAL/path/to/music>:/music \
     --restart unless-stopped \
     ghcr.io/jmbannon/ytdl-sub:latest


Building Docker Image Locally
_____________________________

Run `make docker` in the root directory of this repo to build the image. This
will build the python wheel and install it in the Dockerfile.

Virtualenv
__________

With a Python 3.10 virtual environment, you can clone and install the repo using

.. code-block:: bash

    git clone https://github.com/jmbannon/ytdl-sub.git
    cd ytdl-sub

    pip install -e .

.. _automated_downloads:

Setting Up Automated Downloads
------------------------------
Docker is the recommended way to use ``ytdl-sub`` because it is easy to set up a cron job to
automatically download files via cron job. Setting this up is quite easy since we use the
LinuxServer base image.

Enabling crontab
________________
Crontab is a utility for running cron jobs. To enable it in the docker image, add the following
file to ``/config/custom-services.d/cron``:

.. code-block:: bash

   #!/usr/bin/with-contenv bash
   /usr/sbin/crond -f -S -l 0 -c /etc/crontabs

Creating the crontab file
_________________________
LinuxServer creates the user ``abc`` in the docker container and assigns it the respective
``PUID`` and ``PGID`` permissions to it. We want the cron job to run as this user to ensure
downloaded files get these permissions instead of root permissions.

To do this, we need to create the file ``/etc/crontabs/abc``. Since this path is not part
of the already mounted volume, we need to mount another path. In docker-compose, this looks
like:

.. code-block:: yaml

   services:
     ytdl-sub:
       image: ghcr.io/jmbannon/ytdl-sub:latest
       volumes:
         - </path/to/ytdl-sub/config>:/config
         - </path/to/ytdl-sub/crontab_files>:/etc/crontabs
       ...

Now that ``/path/to/ytdl-sub/crontab_files`` is mounted, we can create the ``abc`` crontab file
there:

.. code-block:: bash

   # min   hour    day     month   weekday command
   */20     *       *       *       *       /config/run_cron

Creating the download script
____________________________

This will run the ``run_cron`` script every 20 minutes. The last step is to create this bash
script in ``/config/run_cron``.

.. code-block:: bash

   #!/bin/bash
   echo "Cron started, running ytdl-sub..."
   ytdl-sub --config=/config/config.yaml sub /config/subscriptions.yaml

Ensure this file is executable and has permissions for ``abc``:

.. code-block:: bash

   # run as root
   chmod +x /config/run_cron
   chown abc:abc /config/run_cron

This will use the :ref:`config_yaml` and download all subscriptions in :ref:`subscription_yaml`.

You're done! You are now downloading your subscriptions every 20 minutes. New channel uploads,
videos added to a playlist, or soundcloud artist uploads can now be downloaded automatically.
