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
from ytdl_sub.entries.youtube import YoutubeChannel
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
            before: "now"
            after: "today-2weeks"

    Adds the override variable ``source_description``, which contains the channel's description.
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

    # pylint: enable=line-too-long

    def __init__(
        self,
        download_options: DownloaderOptionsT,
        enhanced_download_archive: EnhancedDownloadArchive,
        ytdl_options_builder: YTDLOptionsBuilder,
    ):
        super().__init__(
            download_options=download_options,
            enhanced_download_archive=enhanced_download_archive,
            ytdl_options_builder=ytdl_options_builder,
        )
        self.channel: Optional[YoutubeChannel] = None

    def _get_channel(self, entry_dicts: List[Dict]) -> YoutubeChannel:
        return YoutubeChannel(
            entry_dict=self._filter_entry_dicts(entry_dicts, extractor="youtube:tab")[0],
            working_directory=self.working_directory,
        )

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
        self.channel = self._get_channel(entry_dicts=entry_dicts)
        self.add_override_variables(
            override_variables_to_add={
                "source_description": self.channel.kwargs_get("description", "")
            }
        )

        channel_videos = self._filter_entry_dicts(entry_dicts, sort_by="playlist_index")

        # Iterate in descending order to process older videos first. In case an error occurs and a
        # the channel must be redownloaded, it will fetch most recent metadata first, and break
        # on the older video that's been processed and is in the download archive.
        for idx, entry_dict in enumerate(reversed(channel_videos), start=1):
            video = YoutubeVideo(entry_dict=entry_dict, working_directory=self.working_directory)
            download_logger.info("Downloading %d/%d %s", idx, len(entry_dicts), video.title)

            # Re-download the contents even if it's a dry-run as a single video. At this time,
            # channels do not download subtitles or subtitle metadata
            as_single_video_dict = self.extract_info_with_retry(
                is_downloaded_fn=None if self.is_dry_run else video.is_downloaded,
                ytdl_options_overrides={"writeinfojson": False, "skip_download": self.is_dry_run},
                url=video.kwargs("webpage_url"),
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
    ):
        """
        Downloads a thumbnail and stores it in the output directory

        Parameters
        ----------
        thumbnail_url:
            Url of the thumbnail
        output_thumbnail_path:
            Path to store the thumbnail after downloading
        """
        if not thumbnail_url:
            download_logger.warning("Could not find a thumbnail for %s", self.channel.uid)
            return

        convert_url_thumbnail(
            thumbnail_url=thumbnail_url, output_thumbnail_path=output_thumbnail_path
        )

    def post_download(self, overrides: Overrides):
        """
        Downloads and moves channel avatar and banner images to the output directory.

        Parameters
        ----------
        overrides
            Overrides that can contain variables in the avatar or banner file path
        """
        if self.download_options.channel_avatar_path:
            avatar_thumbnail_name = overrides.apply_formatter(
                self.download_options.channel_avatar_path
            )
            self._download_thumbnail(
                thumbnail_url=self.channel.avatar_thumbnail_url(),
                output_thumbnail_path=str(Path(self.working_directory) / avatar_thumbnail_name),
            )
            self.save_file(file_name=avatar_thumbnail_name)

        if self.download_options.channel_banner_path:
            banner_thumbnail_name = overrides.apply_formatter(
                self.download_options.channel_banner_path
            )
            self._download_thumbnail(
                thumbnail_url=self.channel.banner_thumbnail_url(),
                output_thumbnail_path=str(Path(self.working_directory) / banner_thumbnail_name),
            )
            self.save_file(file_name=banner_thumbnail_name)
