Examples
========

This page shows how you can use ytdl-sub for various use cases. These
are the configs I personally use and have incorporated as part of the e2e tests.

Each example has a ``config.yaml`` and ``subscription.yaml``. The config defines
`how` you format your media, whereas the subscription defines `what` you
download plus some additional configuring if needed.

Also note that ``kodi`` examples are applicable for ``jellyfin``, ``emby``, and
``plex`` with the
`XBMC Movies <https://github.com/gboudreau/XBMCnfoMoviesImporter.bundle>`_
or
`XBMC TV Show <https://github.com/gboudreau/XBMCnfoTVImporter.bundle>`_
Plex importer. We would like to improve Plex support, please chime in
`here <https://github.com/jmbannon/ytdl-sub/issues/6>`_
if you have experience with importing custom videos with metadata.

Kodi/Jellyfin TV Shows
----------------------

config.yaml
^^^^^^^^^^^

.. include:: ../examples/kodi_tv_shows_config.yaml
   :literal:

subscriptions.yaml
^^^^^^^^^^^^^^^^^^

.. include:: ../examples/kodi_tv_shows_subscriptions.yaml
   :literal:

Kodi/Jellyfin Music Videos
----------------------

config.yaml
^^^^^^^^^^^

.. include:: ../examples/kodi_music_videos_config.yaml
   :literal:

subscriptions.yaml
^^^^^^^^^^^^^^^^^^

.. include:: ../examples/kodi_music_videos_subscriptions.yaml
   :literal: