from typing import Dict
from typing import Generator
from typing import List

from ytdl_sub.downloaders.generic.collection import CollectionDownloader
from ytdl_sub.downloaders.generic.collection import CollectionDownloadOptions
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
    """

    _required_keys = {"playlist_url"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._playlist_url = self._validate_key(
            "playlist_url", YoutubePlaylistUrlValidator
        ).playlist_url

        self.collection_validator = CollectionDownloadOptions(
            name=self._name,
            value={"urls": [{"url": self._playlist_url}]},
        )

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

    @classmethod
    def added_override_variables(cls) -> List[str]:
        """
        Adds the following :ref:`override <overrides>` variables:

        .. code-block:: yaml

           overrides:
              source_uploader:  # The playlist's owner's channel name. NOTE: sometimes it's empty, use with caution
              source_title:  # The playlist's title
              source_description:  # The playlist's description
        """
        return ["source_uploader", "source_title", "source_description"]

    # pylint: enable=line-too-long

    def download(self) -> Generator[YoutubePlaylistVideo, None, None]:
        """
        Downloads all videos in a Youtube playlist.
        """
        downloader = CollectionDownloader(
            download_options=self.download_options.collection_validator,
            enhanced_download_archive=self._enhanced_download_archive,
            ytdl_options_builder=self._ytdl_options_builder,
            overrides=self.overrides,
        )
        collection_url = self.download_options.collection_validator.collection_urls.list[0]

        parents = downloader.download_url_metadata(collection_url=collection_url)
        assert len(parents) == 1, "Playlist should be the only entry parent"
        playlist = parents[0]

        # TODO: Handle this better
        self.overrides.add_override_variables(
            variables_to_add={
                "source_title": playlist.title,
                "source_uploader": playlist.kwargs_get("uploader", "__failed_to_scrape__"),
                "source_description": playlist.kwargs_get("description", ""),
            }
        )

        for entry in downloader.download_url(collection_url=collection_url, parents=parents):
            # pylint: disable=protected-access
            yield YoutubePlaylistVideo(
                entry_dict=entry._kwargs, working_directory=self.working_directory
            )
            # pylint: enable=protected-access
