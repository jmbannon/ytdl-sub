Getting Started
===============

The goal of this app is automate the downloading and metadata creation of audio and video files, then place the files
in a directory that gets read by your media player/server. Everyone stores and watches their media differently, so
we strive for comprehensive and simplistic customization to fit all self-hosting needs.

Audio metadata is just a matter of adding tags to the audio file. The backend plugin we use supports practically every
common audio file type, so there should (hopefully) be no issues getting audio recognized by your media player.

Video metadata on the other hand, is currently geared toward generating Kodi/Jellyfin/Emby NFO files. Plex uses metadata
written within MP4 containers - we do not support that currently, but could be added as a plugin in the future.

.. toctree::
   :titlesonly:
   :maxdepth: 2

   usage_ideas
   install
