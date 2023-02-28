from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from ytdl_sub.config.preset import Preset
from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.plugins.audio_extract import AudioExtractPlugin
from ytdl_sub.plugins.chapters import ChaptersPlugin
from ytdl_sub.plugins.date_range import DateRangePlugin
from ytdl_sub.plugins.file_convert import FileConvertPlugin
from ytdl_sub.plugins.match_filters import MatchFiltersPlugin
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.subtitles import SubtitlesPlugin
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

PluginT = TypeVar("PluginT", bound=Plugin)


class SubscriptionYTDLOptions:
    def __init__(
        self,
        preset: Preset,
        plugins: List[Plugin],
        enhanced_download_archive: EnhancedDownloadArchive,
        working_directory: str,
        dry_run: bool,
    ):
        self._preset = preset
        self._plugins = plugins
        self._enhanced_download_archive = enhanced_download_archive
        self._working_directory = working_directory
        self._dry_run = dry_run

    def _get_plugin(self, plugin_type: Type[PluginT]) -> Optional[PluginT]:
        for plugin in self._plugins:
            if isinstance(plugin, plugin_type):
                return plugin
        return None

    @property
    def _downloader(self) -> Type[Downloader]:
        return self._preset.downloader

    @property
    def _global_options(self) -> Dict:
        """
        Returns
        -------
        ytdl-options to apply to every run no matter what
        """
        ytdl_options = {
            # Download all files in the format of {id}.{ext}
            "outtmpl": str(Path(self._working_directory) / "%(id)s.%(ext)s"),
            # Always write thumbnails
            "writethumbnail": True,
            "ffmpeg_location": FFMPEG.ffmpeg_path(),
        }

        return ytdl_options

    @property
    def _dry_run_options(self) -> Dict:
        return {
            "skip_download": True,
            "writethumbnail": False,
        }

    @property
    def _info_json_only_options(self) -> Dict:
        return {
            "skip_download": True,
            "writethumbnail": False,
            "writeinfojson": True,
        }

    @property
    def _output_options(self) -> Dict:
        ytdl_options = {}

        if (
            self._downloader.supports_download_archive
            and self._preset.output_options.maintain_download_archive
        ):
            ytdl_options["download_archive"] = str(
                Path(self._working_directory) / self._enhanced_download_archive.archive_file_name
            )

        return ytdl_options

    def _plugin_ytdl_options(self, plugin: Type[PluginT]) -> Dict:
        if not (audio_extract_plugin := self._get_plugin(plugin)):
            return {}

        return audio_extract_plugin.ytdl_options()

    @property
    def _user_ytdl_options(self) -> Dict:
        return self._preset.ytdl_options.dict

    def metadata_builder(self) -> YTDLOptionsBuilder:
        """
        Returns
        -------
        YTDLOptionsBuilder
            Builder with values set for fetching metadata (.info.json) only
        """
        return YTDLOptionsBuilder().add(
            self._global_options,
            self._output_options,
            self._plugin_ytdl_options(DateRangePlugin),
            self._plugin_ytdl_options(MatchFiltersPlugin),
            self._user_ytdl_options,  # user ytdl options...
            self._info_json_only_options,  # then info_json_only options
        )

    def download_builder(self) -> YTDLOptionsBuilder:
        """
        Returns
        -------
        YTDLOptionsBuilder
            Builder with values set based on the subscription for actual downloading
        """
        ytdl_options_builder = YTDLOptionsBuilder().add(
            self._global_options,
            self._output_options,
            self._plugin_ytdl_options(DateRangePlugin),
            self._plugin_ytdl_options(FileConvertPlugin),
            self._plugin_ytdl_options(SubtitlesPlugin),
            self._plugin_ytdl_options(ChaptersPlugin),
            self._plugin_ytdl_options(AudioExtractPlugin),
            self._user_ytdl_options,  # user ytdl options...
        )
        # Add dry run options last if enabled
        if self._dry_run:
            ytdl_options_builder.add(self._dry_run_options)

        return ytdl_options_builder
