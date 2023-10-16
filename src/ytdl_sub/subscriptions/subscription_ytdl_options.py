from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from yt_dlp import match_filter_func

from ytdl_sub.config.plugin import Plugin
from ytdl_sub.config.preset import Preset
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.plugins.audio_extract import AudioExtractPlugin
from ytdl_sub.plugins.chapters import ChaptersPlugin
from ytdl_sub.plugins.file_convert import FileConvertPlugin
from ytdl_sub.plugins.format import FormatPlugin
from ytdl_sub.plugins.match_filters import MatchFiltersPlugin
from ytdl_sub.plugins.match_filters import combine_filters
from ytdl_sub.plugins.match_filters import default_filters
from ytdl_sub.plugins.subtitles import SubtitlesPlugin
from ytdl_sub.utils.ffmpeg import FFMPEG
from ytdl_sub.utils.logger import Logger
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

PluginT = TypeVar("PluginT", bound=Plugin)

logger = Logger.get("ytdl-options")


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
    def _download_only_options(self) -> Dict:
        return {"break_on_reject": True}

    @property
    def _output_options(self) -> Dict:
        ytdl_options = {}

        if self._preset.output_options.maintain_download_archive:
            ytdl_options["download_archive"] = self._enhanced_download_archive.working_file_path

        return ytdl_options

    def _plugin_ytdl_options(self, plugin: Type[PluginT]) -> Dict:
        if plugin_obj := self._get_plugin(plugin):
            return plugin_obj.ytdl_options()

        return {}

    @property
    def _user_ytdl_options(self) -> Dict:
        return self._preset.ytdl_options.dict

    @property
    def _plugin_match_filters(self) -> Dict:
        """
        All match-filters from every plugin to fetch metadata.
        In order for other plugins to not collide with user-defined match-filters, do

        match_filters = user_match_filters or {}
        for plugin in plugins:
          for filter in match_filters:
            AND plugin's match filters onto the existing filters

        Otherwise, the filters separately act as an OR
        """
        match_filters, breaking_match_filters = default_filters()

        match_filters_plugin = self._get_plugin(MatchFiltersPlugin)
        if match_filters_plugin:
            (
                user_match_filters,
                user_breaking_match_filters,
            ) = match_filters_plugin.ytdl_options_match_filters()
            match_filters = combine_filters(filters=user_match_filters, to_combine=match_filters)
            breaking_match_filters = combine_filters(
                filters=user_breaking_match_filters, to_combine=breaking_match_filters
            )

        for plugin in self._plugins:
            # Do not re-add original match-filters plugin
            if isinstance(plugin, MatchFiltersPlugin):
                continue

            pl_match_filters, pl_breaking_match_filters = plugin.ytdl_options_match_filters()

            match_filters = combine_filters(filters=match_filters, to_combine=pl_match_filters)
            breaking_match_filters = combine_filters(
                filters=breaking_match_filters, to_combine=pl_breaking_match_filters
            )

        logger.debug(
            "Setting match-filters: %s",
            "\n - ".join([""] + match_filters) if match_filters else "[]",
        )
        logger.debug(
            "Setting breaking-match-filters: %s",
            "\n - ".join([""] + breaking_match_filters) if breaking_match_filters else "[]",
        )
        return {
            "match_filter": match_filter_func(
                filters=match_filters, breaking_filters=breaking_match_filters
            )
        }

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
            self._plugin_match_filters,
            self._plugin_ytdl_options(FormatPlugin),
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
            self._plugin_ytdl_options(FileConvertPlugin),
            self._plugin_ytdl_options(SubtitlesPlugin),
            self._plugin_ytdl_options(ChaptersPlugin),
            self._plugin_ytdl_options(AudioExtractPlugin),
            self._plugin_ytdl_options(FormatPlugin),
            self._user_ytdl_options,  # user ytdl options...
            self._download_only_options,  # then download_only options
        )
        # Add dry run options last if enabled
        if self._dry_run:
            ytdl_options_builder.add(self._dry_run_options)

        return ytdl_options_builder
