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

Virtualenv
__________
With a Python 3.10 virtual environment, you can clone and install the repo using

.. code-block:: shell

   git clone https://github.com/jmbannon/ytdl-sub.git
   cd ytdl-sub

   pip install -e .

Local Docker
____________
If you are familiar with
`LinuxServer.io <https://www.linuxserver.io/>`_,
you will be happy to hear that we use their base image for our docker image.
Documentation on how to build the image locally can be found in the repo's
`docker readme <https://github.com/jmbannon/ytdl-sub/tree/master/docker#running-ytdl-sub-in-docker>`_.


