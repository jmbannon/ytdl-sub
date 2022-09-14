from pathlib import Path
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.downloaders.downloader import DownloaderOptionsT
from ytdl_sub.downloaders.downloader import download_logger
from ytdl_sub.downloaders.youtube.abc import YoutubeDownloader
from ytdl_sub.downloaders.youtube.abc import YoutubeDownloaderOptions
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry_parent import EntryParent
from ytdl_sub.entries.youtube import YoutubeVideo
from ytdl_sub.utils.datetime import to_date_range_hack
from ytdl_sub.utils.thumbnail import convert_url_thumbnail
from ytdl_sub.validators.string_datetime import StringDatetimeValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.url_validator import YoutubeChannelUrlValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class YoutubeChannelDownloaderOptions(YoutubeDownloaderOptions):
    """
    Downloads all videos from a youtube channel.

    Usage:

    .. code-block:: yaml

      presets:
        my_example_preset:
          youtube:
            # required
            download_strategy: "channel"
            channel_url: "UCsvn_Po0SmunchJYtttWpOxMg"
            # optional
            channel_avatar_path: "poster.jpg"
            channel_banner_path: "fanart.jpg"
    """

    _required_keys = {"channel_url"}
    _optional_keys = {
        "before",
        "after",
        "channel_avatar_path",
        "channel_banner_path",
    }

    def __init__(self, name, value):
        super().__init__(name, value)
        self._channel_url = self._validate_key(
            "channel_url", YoutubeChannelUrlValidator
        ).channel_url
        self._channel_avatar_path = self._validate_key_if_present(
            "channel_avatar_path", OverridesStringFormatterValidator
        )
        self._channel_banner_path = self._validate_key_if_present(
            "channel_banner_path", OverridesStringFormatterValidator
        )
        self._before = self._validate_key_if_present("before", StringDatetimeValidator)
        self._after = self._validate_key_if_present("after", StringDatetimeValidator)

    @property
    def channel_url(self) -> str:
        """
        Required. The channel's url, i.e.
        ``https://www.youtube.com/channel/UCsvn_Po0SmunchJYOWpOxMg``. URLs with ``/username`` or
        ``/c`` are valid to use.
        """
        return self._channel_url

    @property
    def channel_avatar_path(self) -> Optional[OverridesStringFormatterValidator]:
        """
        Optional. Path to store the channel's avatar thumbnail image to.
        """
        return self._channel_avatar_path

    @property
    def channel_banner_path(self) -> Optional[OverridesStringFormatterValidator]:
        """
        Optional. Path to store the channel's banner image to.
        """
        return self._channel_banner_path

    @property
    def before(self) -> Optional[StringDatetimeValidator]:
        """
        DEPRECATED: use the `date_range` plugin instead. Will be removed in version 0.5.0
        Optional. Only download videos before this datetime.
        """
        return self._before

    @property
    def after(self) -> Optional[StringDatetimeValidator]:
        """
        DEPRECATED: use the `date_range` plugin instead. Will be removed in version 0.5.0
        Optional. Only download videos after this datetime.
        """
        return self._after


class YoutubeChannelDownloader(YoutubeDownloader[YoutubeChannelDownloaderOptions, YoutubeVideo]):
    downloader_options_type = YoutubeChannelDownloaderOptions
    downloader_entry_type = YoutubeVideo

    # pylint: disable=line-too-long
    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        Default `ytdl_options`_ for ``channel``

        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
             break_on_existing: True  # stop downloads (newest to oldest) if a video is already downloaded
             break_on_reject: True  # stops downloads if the video's upload date is out of the specified 'before'/'after' range
        """
        return dict(
            super().ytdl_option_defaults(),
            **{
                "break_on_existing": True,
                "break_on_reject": True,
            },
        )

    @classmethod
    def added_override_variables(cls) -> List[str]:
        """
        Adds the following :ref:`override <overrides>` variables:

        .. code-block:: yaml

           overrides:
              source_uploader:  # The channel's name. NOTE: sometimes it's empty, use with caution
              source_title:  # The channel's name
              source_description:  # The channel's description
        """
        return ["source_uploader", "source_title", "source_description"]

    # pylint: enable=line-too-long

    def __init__(
        self,
        download_options: DownloaderOptionsT,
        enhanced_download_archive: EnhancedDownloadArchive,
        ytdl_options_builder: YTDLOptionsBuilder,
        overrides: Overrides,
    ):
        super().__init__(
            download_options=download_options,
            enhanced_download_archive=enhanced_download_archive,
            ytdl_options_builder=ytdl_options_builder,
            overrides=overrides,
        )

        self.channel: Optional[EntryParent] = None

    def download(self) -> Generator[YoutubeVideo, None, None]:
        """
        Downloads all videos from a channel
        """
        ytdl_options_overrides = {}

        # If a date range is specified when download a YT channel, add it into the ytdl options
        source_date_range = to_date_range_hack(
            before=self.download_options.before, after=self.download_options.after
        )
        if source_date_range:
            ytdl_options_overrides["daterange"] = source_date_range

        # dry-run the entire channel download first, this will get the
        # videos that will be downloaded. Afterwards, download each video one-by-one
        entry_dicts = self.extract_info_via_info_json(
            ytdl_options_overrides=ytdl_options_overrides,
            only_info_json=True,
            log_prefix_on_info_json_dl="Downloading metadata for",
            url=self.download_options.channel_url,
        )

        parents: List[EntryParent] = EntryParent.from_entry_dicts(
            entry_dicts=entry_dicts,
            working_directory=self.working_directory,
        )
        assert len(parents) == 1, "Channel should be the only parent"
        self.channel = parents[0]

        self.overrides.add_override_variables(
            variables_to_add={
                "source_uploader": self.channel.kwargs_get("uploader", "__failed_to_scrape__"),
                "source_title": self.channel.kwargs("title"),
                "source_description": self.channel.kwargs_get("description", ""),
            }
        )

        # Iterate in descending order to process older videos first. In case an error occurs and a
        # the channel must be redownloaded, it will fetch most recent metadata first, and break
        # on the older video that's been processed and is in the download archive.
        for idx, video in enumerate(reversed(self.channel.child_entries), start=1):
            video = video.to_type(YoutubeVideo)
            download_logger.info("Downloading %d/%d %s", idx, self.channel.child_count, video.title)

            # Re-download the contents even if it's a dry-run as a single video. At this time,
            # channels do not download subtitles or subtitle metadata
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

    def _download_thumbnail(
        self,
        thumbnail_url: str,
        output_thumbnail_path: str,
    ) -> Optional[bool]:
        """
        Downloads a thumbnail and stores it in the output directory

        Parameters
        ----------
        thumbnail_url:
            Url of the thumbnail
        output_thumbnail_path:
            Path to store the thumbnail after downloading

        Returns
        -------
        True if the thumbnail converted. None if it is missing or failed.
        """
        if not thumbnail_url:
            download_logger.warning("Could not find a thumbnail for %s", self.channel.uid)
            return None

        return convert_url_thumbnail(
            thumbnail_url=thumbnail_url, output_thumbnail_path=output_thumbnail_path
        )

    def post_download(self):
        """
        Downloads and moves channel avatar and banner images to the output directory.
        """
        if self.download_options.channel_avatar_path:
            avatar_thumbnail_name = self.overrides.apply_formatter(
                self.download_options.channel_avatar_path
            )
            if self._download_thumbnail(
                thumbnail_url=self.channel.get_thumbnail_url("avatar_uncropped"),
                output_thumbnail_path=str(Path(self.working_directory) / avatar_thumbnail_name),
            ):
                self.save_file(file_name=avatar_thumbnail_name)
            else:
                download_logger.warning("Failed to download channel's avatar image")

        if self.download_options.channel_banner_path:
            banner_thumbnail_name = self.overrides.apply_formatter(
                self.download_options.channel_banner_path
            )
            if self._download_thumbnail(
                thumbnail_url=self.channel.get_thumbnail_url("banner_uncropped"),
                output_thumbnail_path=str(Path(self.working_directory) / banner_thumbnail_name),
            ):
                self.save_file(file_name=banner_thumbnail_name)
            else:
                download_logger.warning("Failed to download channel's banner image")
