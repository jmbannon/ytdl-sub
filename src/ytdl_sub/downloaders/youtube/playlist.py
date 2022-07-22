from typing import Dict
from typing import Generator

from ytdl_sub.downloaders.youtube.abc import YoutubeDownloader
from ytdl_sub.downloaders.youtube.abc import YoutubeDownloaderOptions
from ytdl_sub.entries.youtube import YoutubePlaylistVideo
from ytdl_sub.validators.url_validator import YoutubePlaylistUrlValidator


class YoutubePlaylistDownloaderOptions(YoutubeDownloaderOptions):
    """
    Downloads all videos from a youtube playlist.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          youtube:
            # required
            download_strategy: "playlist"
            playlist_url: "https://www.youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg"
            # optional
            download_individually: True
    """

    _required_keys = {"playlist_url"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._playlist_url = self._validate_key(
            "playlist_url", YoutubePlaylistUrlValidator
        ).playlist_url

    @property
    def playlist_url(self) -> str:
        """
        Required. The playlist's url, i.e.
        ``https://www.youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg``.
        """
        return self._playlist_url


class YoutubePlaylistDownloader(
    YoutubeDownloader[YoutubePlaylistDownloaderOptions, YoutubePlaylistVideo]
):
    downloader_options_type = YoutubePlaylistDownloaderOptions
    downloader_entry_type = YoutubePlaylistVideo

    # pylint: disable=line-too-long
    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        Default `ytdl_options`_ for ``playlist``

        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
             break_on_existing: True  # stop downloads (newest to oldest) if a video is already downloaded
        """
        return dict(
            super().ytdl_option_defaults(),
            **{"break_on_existing": True},
        )

    # pylint: enable=line-too-long

    def download(self) -> Generator[YoutubePlaylistVideo, None, None]:
        """
        Downloads all videos in a Youtube playlist.

        Dry-run the entire playlist download first. This will get the videos that will be
        downloaded. Afterwards, download each video one-by-one
        """
        entry_dicts = self.extract_info_via_info_json(
            ytdl_options_overrides={
                "skip_download": True,
                "writethumbnail": False,
            },
            url=self.download_options.playlist_url,
        )

        for entry_dict in entry_dicts:
            if entry_dict.get("extractor") == "youtube":

                # Only do the individual download if it is not dry-run and downloading individually
                if not self.is_dry_run:
                    _ = self.extract_info(
                        ytdl_options_overrides={
                            "playlist_items": str(entry_dict.get("playlist_index")),
                            "writeinfojson": False,
                        },
                        url=self.download_options.playlist_url,
                    )

                yield YoutubePlaylistVideo(
                    entry_dict=entry_dict, working_directory=self.working_directory
                )
