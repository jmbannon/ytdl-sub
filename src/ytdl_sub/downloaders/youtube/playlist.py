from typing import Dict
from typing import Generator
from typing import List

from ytdl_sub.downloaders.downloader import download_logger
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

        Dry-run the entire playlist download first. This will get the videos that will be
        downloaded. Afterwards, download each video one-by-one
        """
        entry_dicts = self.extract_info_via_info_json(
            only_info_json=True,
            log_prefix_on_info_json_dl="Downloading metadata for",
            url=self.download_options.playlist_url,
        )

        playlist = self._filter_entry_dicts(entry_dicts, extractor="youtube:tab")[0]
        playlist_videos = self._filter_entry_dicts(entry_dicts, sort_by="playlist_index")

        self.overrides.add_override_variables(
            variables_to_add={
                "source_title": playlist["title"],
                "source_uploader": playlist.get("uploader", "__failed_to_scrape__"),
                "source_description": playlist.get("description", ""),
            }
        )

        # Iterate in reverse order to process older videos first. In case an error occurs and a
        # the playlist must be redownloaded, it will fetch most recent metadata first, and break
        # on the older video that's been processed and is in the download archive.
        for idx, entry_dict in enumerate(reversed(playlist_videos), start=1):
            video = YoutubePlaylistVideo(
                entry_dict=entry_dict, working_directory=self.working_directory
            )
            download_logger.info("Downloading %d/%d %s", idx, len(entry_dicts), video.title)

            # Re-download the contents even if it's a dry-run as a single video. At this time,
            # playlists do not download subtitles or subtitle metadata
            as_single_video_dict = self.extract_info_with_retry(
                is_downloaded_fn=None if self.is_dry_run else video.is_downloaded,
                ytdl_options_overrides={"writeinfojson": False, "skip_download": self.is_dry_run},
                url=video.webpage_url,
            )

            # Workaround for the ytdlp issue
            # pylint: disable=protected-access
            video._kwargs["requested_subtitles"] = as_single_video_dict.get("requested_subtitles")
            # pylint: enable=protected-access

            yield video
