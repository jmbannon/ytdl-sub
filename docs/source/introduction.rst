What is ytdl-sub?
=================

.. _yt-dlp: https://github.com/yt-dlp/yt-dlp
.. _kodi: https://github.com/xbmc/xbmc
.. _jellyfin: https://github.com/jellyfin/jellyfin
.. _plex: https://github.com/plexinc/pms-docker
.. _emby: https://github.com/plexinc/pms-docker

``ytdl-sub`` is a command-line tool that downloads media via `yt-dlp`_ and prepares it for your favorite media player (`Kodi`_, `Jellyfin`_, `Plex`_, `Emby`_, modern music players).

Visual examples
---------------

.. figure:: https://user-images.githubusercontent.com/10107080/182677243-b4184e51-9780-4094-bd40-ea4ff58555d0.PNG

    Youtube channels as TV shows in Jellyfin

.. figure:: https://user-images.githubusercontent.com/10107080/182677256-43aeb029-0c3f-4648-9fd2-352b9666b262.PNG

    Music videos and concerts in Jellyfin

.. figure:: https://user-images.githubusercontent.com/10107080/182677268-d1bf2ff0-9b9c-4a04-98ec-443a67ada734.png

    Music videos and concerts in Kodi

.. figure:: https://user-images.githubusercontent.com/10107080/182685415-06adf477-3dd3-475d-bbcd-53b0152b9f0a.PNG

    SoundCloud albums and singles in MusicBee


Why ytdl-sub?
-------------
There is a lack of open-source tools to download media and generate metadata to play it in these players. Most solutions involve using multiple tools or bash scripts to achieve this. ``ytdl-sub`` aims to consolidate all of this logic into a single easy-to-use application that can run automatically once configured.

Why download instead of stream?
-------------------------------
We believe it is important to download what you like because there is no guarantee it will stay online forever. We also believe it is important to download it in such a way that it is easy to consume. Most solutions today force you to watch/listen to your downloaded content via file system or web browser. ``ytdl-sub`` aims to format downloaded content for any media player.