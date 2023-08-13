from ytdl_sub.downloaders.url.validators import UrlValidator


# TODO: Remove later - keep for docstring
class UrlDownloadOptions(UrlValidator):
    """
    Downloads from a single URL supported by yt-dlp.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          download:
            # required
            url: "youtube.com/channel/UCsvn_Po0SmunchJYtttWpOxMg"
            # optional
            playlist_thumbnails:
              - name: "poster.jpg"
                uid: "avatar_uncropped"
              - name: "fanart.jpg"
                uid: "banner_uncropped"
            download_reverse: True
    """
