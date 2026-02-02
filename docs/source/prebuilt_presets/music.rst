=============
Music Presets
=============

Music downloadable by yt-dlp comes in many flavors. ``ytdl-sub`` offers a suite of
various presets for handling some of the most popular forms of uploaded music content.


YouTube Releases
----------------

Many artists, especially those auto-uploaded as ``Topics`` in YouTube have a section on
their channel named "Releases", or "Albums and Singles". The ``YouTube Releases`` preset
aims to scrape this *playlist of playlists*.

Playlists are recognized as the album, and videos within it are tracks.

.. code-block:: yaml

   YouTube Releases:
     = Jazz:  # Sets genre tag to "Jazz"
       "Thelonious Monk": "https://www.youtube.com/@officialtheloniousmonk/releases"

If you are only interested in a subset of albums, you can provide their playlists as
separate values in the form of an array, like so:

.. code-block:: yaml

   YouTube Releases:
     = Jazz:
       "Thelonious Monk":
         - "https://www.youtube.com/playlist?list=OLAK5uy_lcqINwfzkw73TPnAt6MlpB6V0gM9VzQu8"  # Monk on Monk
         - "https://www.youtube.com/playlist?list=OLAK5uy_nhuvjuZOO3yLIWCbQzbiWfyzkGapSIuYw"  # Late Night Thelonious Monk


YouTube Full Albums
-------------------

In many cases, albums are uploaded to YouTube as a single video, where each track as
separated by either chapters or timestamps in a description. The ``YouTube Full Albums``
preset will take each video and split it by the chapters to form an album.

Videos are recognized as the album, and chapters within it are tracks.

.. code-block:: yaml

   YouTube Full Albums:
     = Lofi:
       "Game Chops": "https://www.youtube.com/playlist?list=PLBsm_SagFMmdWnCnrNtLjA9kzfrRkto4i"

If you are only interested in a subset of albums, you can provide their video as
separate values in the form of an array, like so:

.. code-block:: yaml

   YouTube Full Albums:
     = Lofi:
       "Game Chops":
         - "https://www.youtube.com/watch?v=m7vBrD7LMLI"  # Zelda & Sleep Ensemble Collection
         - "https://www.youtube.com/watch?v=w0XebCwSpKI"  # Study Buddy ~ video game lofi mix


Soundcloud Discography
----------------------

SoundCloud tracks can be uploaded as either a single, part of an album, or a
collaboration with another artist. At this time, ``SoundCloud Discography`` only scrapes
singles and albums.  It will attempt to group tracks into albums before falling back to
single format.

.. code-block:: yaml

   SoundCloud Discography:
     = Chill Hop:
       "UKNOWY": "https://soundcloud.com/uknowymunich"
     = Synthwave:
       "Lazerdiscs Records": "https://soundcloud.com/lazerdiscsrecords"
       "Earmake": "https://soundcloud.com/earmake"


Bandcamp
--------

Bandcamp albums and singles can be scraped using the ``Bandcamp`` preset.

.. code-block:: yaml

   Bandcamp:
     = Lofi:
       "Emily Hopkins": "https://emilyharpist.bandcamp.com/"
