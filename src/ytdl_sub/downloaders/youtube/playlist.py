from typing import Dict
from typing import Generator
from typing import Optional

from ytdl_sub.downloaders.youtube.abc import YoutubeDownloader
from ytdl_sub.downloaders.youtube.abc import YoutubeDownloaderOptions
from ytdl_sub.entries.youtube import YoutubePlaylistVideo
from ytdl_sub.validators.url_validator import YoutubePlaylistUrlValidator
from ytdl_sub.validators.validators import BoolValidator


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
    _optional_keys = {"download_individually"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._playlist_url = self._validate_key(
            "playlist_url", YoutubePlaylistUrlValidator
        ).playlist_url
        self._download_individually = self._validate_key_if_present(
            "download_individually", BoolValidator, default=True
        )

    @property
    def playlist_url(self) -> str:
        """
        Required. The playlist's url, i.e.
        ``https://www.youtube.com/playlist?list=UCsvn_Po0SmunchJYtttWpOxMg``.
        """
        return self._playlist_url

    @property
    def download_individually(self) -> Optional[bool]:
        """
        Optional. Downloads files from the playlist individually instead of in bulk. Setting to True
        is safer when downloading large amounts of videos in case an error occurs. Downloading by
        bulk (by setting to False) can increase speeds. Defaults to True.
        """
        return self._download_individually.value


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
        Downloads all videos in a Youtube playlist
        """
        ytdl_options_overrides = {}

        # If downloading individually, dry-run the entire channel download first, this will get the
        # videos that will be downloaded. Afterwards, download each video one-by-one
        if self.download_options.download_individually:
            ytdl_options_overrides["skip_download"] = True
            ytdl_options_overrides["writethumbnail"] = False

        entry_dicts = self.extract_info_via_info_json(
            ytdl_options_overrides=ytdl_options_overrides, url=self.download_options.playlist_url
        )

        for entry_dict in entry_dicts:
            if entry_dict.get("extractor") == "youtube":

                # Only do the individual download if it is not dry-run and downloading individually
                if not self.is_dry_run and self.download_options.download_individually:
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
