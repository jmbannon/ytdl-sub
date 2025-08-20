=================
What is ytdl-sub?
=================

.. _yt-dlp: https://github.com/yt-dlp/yt-dlp
.. _kodi: https://github.com/xbmc/xbmc
.. _jellyfin: https://github.com/jellyfin/jellyfin
.. _plex: https://github.com/plexinc/pms-docker
.. _emby: https://github.com/plexinc/pms-docker

``ytdl-sub`` is a command-line tool that builds on and orchestrates `yt-dlp`_ to
download media from YouTube and/or other online services. It provides a declarative,
expressive YAML configuration system that allows you to describe which media to download
and how it should appear in your media library servers and applications such as
`Jellyfin`_, `Plex`_, `Emby`_, `Kodi`_, modern music players, etc..

To these ends, ``ytdl-sub``:

- wraps and runs `yt-dlp`_, per your configuration to:

  - download the media, remux and/or optionally transcode it

- prepares additional metadata both embedded and in external files

- renames the resulting files

- places them in your library

.. figure:: https://user-images.githubusercontent.com/10107080/182677243-b4184e51-9780-4094-bd40-ea4ff58555d0.PNG
  :alt: The Jellyfin web interface, showing the thumbnails of various YouTube shows.

  Youtube channels as TV shows in Jellyfin

.. figure:: https://user-images.githubusercontent.com/10107080/182677256-43aeb029-0c3f-4648-9fd2-352b9666b262.PNG
  :alt: The Jellyfin web interace, showing the thumbnails of various music videos starring the Red Hot Chili Peppers

  Music videos and concerts in Jellyfin

.. figure:: https://user-images.githubusercontent.com/10107080/182677268-d1bf2ff0-9b9c-4a04-98ec-443a67ada734.png
  :alt: The Kodi app interface, showing a list of artists available to watch under the "Music videos" heading

  Music videos and concerts in Kodi

.. figure:: https://user-images.githubusercontent.com/10107080/182685415-06adf477-3dd3-475d-bbcd-53b0152b9f0a.PNG
  :alt: The MusicBee app interface, showing a list of album artists and the thumbnails of all downloaded songs produced by the currently selected artist

  SoundCloud albums and singles in MusicBee


Motivation
----------

`yt-dlp`_ has grown into a well maintained, central repository of the intricate,
inscrutable, and extensive technical knowledge required to automate downloading media
from online services. When those services change their APIs or otherwise change
behavior, `yt-dlp`_ is the central, low-level tool to update. It does a best-in-class
job at that task, and it does that job more effectively by narrowing focus to just that.
As much knowledge as it encapsulates and as well as it does that, it still requires a
great deal of additional knowledge to make its output accessible to end-users. Mostly
this gap is about extracting and formatting metadata and correctly placing the resulting
output files in a media library.

A number of tools, applications, and other projects have grown up around that central
`yt-dlp`_ pillar to fill in those gaps, and this project was one of the early
entrants. Many are `full-featured services that provide web UIs`_ including some that
`provide media player web UIs`_. Most of those other projects necessarily narrow their
scope to provide a more polished and integrated user experience.

Similarly, ``ytdl-sub`` can run automatically to accomplish the same goals, but aims to
serve users that need lower-level control and/or have use cases not covered by the more
narrow scope of those other projects. To some degree, this makes this project
intrinsically less user friendly and requires more technical experience or learning.

Want something that "Just Works", try one of the other projects; we recommend
`Pinchflat`_ as the next step towards that end. Want to download from more than just
YouTube? Don't like the other restrictions inherent in the goals of those other
projects? Have unique use cases? Then dig in, learn, and we hope ``ytdl-sub`` gives you
enough rope and `a foot-gun`_ to get you there.

.. _`full-featured services that provide web UIs`:
   https://github.com/kieraneglin/pinchflat
.. _`provide media player web UIs`:
   https://www.tubearchivist.com/
.. _`Pinchflat`: `full-featured services that provide web UIs`_
.. _`a foot-gun`: https://en.wiktionary.org/wiki/footgun


Why download instead of stream?
-------------------------------

Most of the tools in this `yt-dlp`_ ecosystem serve a similar set of larger, more
general use cases, and so does ``ytdl-sub``:

- Don't rely on profit-driven corporate persons to keep more obscure content available.
- Even if they do, don't depend on them to make it possible to use it in different ways.
- Even when you pay, don't count on them not inserting ads later.
- Regardless, don't depend on them to curate content for yourself and/or your family.
- Free yourself and/or your family from what the algorithm would feed them next.
