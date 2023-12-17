Initial Subscription
====================

Your first subscription should look similar to the below:

.. code-block:: yaml
    
    "My Favorite YouTube Channels":
        "Rick Astley": "https://www.youtube.com/@RickAstleyYT/videos"

The first line in this subscription file is the ``preset``, which provides the "definitions" for the subscription as listed in :doc:`/guides/getting_started/first_config`.

The second line is the actual ``subscription``, named ``Rick Astley``, with a link to a :yt-dlp:`yt-dlp supported site <blob/master/supportedsites.md>`, in this case a YouTube channel.