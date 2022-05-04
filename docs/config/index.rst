Configuration
=============


Source and Download Strategy
----------------------------
Download strategies dictate what exactly is getting downloaded from which
source. By having separate strategies, we can define strategy-dependent
parameters to better fine-tune how we download things.

youtube: channel
^^^^^^^^^^^^^^^^
.. autoclass:: ytdl_sub.downloaders.youtube_downloader.YoutubeChannelDownloaderOptions()
   :members:
   :inherited-members:
   :exclude-members: get_date_range

youtube: playlist
^^^^^^^^^^^^^^^^^
.. autoclass:: ytdl_sub.downloaders.youtube_downloader.YoutubePlaylistDownloaderOptions()
   :members:
   :inherited-members:

youtube: video
^^^^^^^^^^^^^^
.. autoclass:: ytdl_sub.downloaders.youtube_downloader.YoutubeVideoDownloaderOptions()
   :members:
   :inherited-members:

soundcloud: albums_and_singles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: ytdl_sub.downloaders.soundcloud_downloader.SoundcloudAlbumsAndSinglesDownloadOptions()
   :members:
   :inherited-members:

.. toctree::
   :titlesonly:
   :maxdepth: 2

   format_variables/index
   examples/index
