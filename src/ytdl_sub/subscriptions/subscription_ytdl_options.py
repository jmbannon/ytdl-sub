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
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.subtitles import SubtitleOptions
from ytdl_sub.plugins.subtitles import SubtitlesPlugin
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
            "outtmpl": str(Path(self._working_directory) / "%(id)s.%(ext)s")
        }

        if (
            self._downloader.supports_download_archive
            and self._preset.output_options.maintain_download_archive
        ):
            ytdl_options["download_archive"] = str(
                Path(self._working_directory) / self._enhanced_download_archive.archive_file_name
            )

        return ytdl_options

    @property
    def _dry_run_options(self) -> Dict:
        return {
            "skip_download": True,
            "writethumbnail": False,
            # TODO: find a way to not write subtitles; using `simulate: True` breaks tests
        }

    @property
    def _output_options(self) -> Dict:
        ytdl_options = {}
        output_options = self._preset.output_options

        if output_options.thumbnail_name:
            ytdl_options["writethumbnail"] = True

        return ytdl_options

    @property
    def _audio_extract_options(self) -> Dict:
        if not (audio_extract_plugin := self._get_plugin(AudioExtractPlugin)):
            return {}

        return audio_extract_plugin.ytdl_options()

    @property
    def _subtitle_options(self) -> Dict:
        if not (subtitle_plugin := self._get_plugin(SubtitlesPlugin)):
            return {}

        if not self._downloader.supports_subtitles:
            # TODO: warn here
            return {}

        # TODO: Use subtitle ytdl_options
        builder = YTDLOptionsBuilder().add({"writesubtitles": True})
        subtitle_options: SubtitleOptions = subtitle_plugin.plugin_options

        if subtitle_options.embed_subtitles:
            builder.add(
                {"postprocessors": [{"key": "FFmpegEmbedSubtitle", "already_have_subtitle": True}]}
            )

        if subtitle_options.subtitles_name:
            builder.add(
                {
                    "postprocessors": [
                        {
                            "key": "FFmpegSubtitlesConvertor",
                            "format": subtitle_options.subtitles_type,
                        }
                    ],
                }
            )

        # If neither subtitles_name or embed_subtitles is set, do not set any other flags
        if not builder.to_dict():
            return {}

        builder.add(
            {
                "writeautomaticsub": subtitle_options.allow_auto_generated_subtitles,
                "subtitleslangs": subtitle_options.languages,
            }
        )

        return builder.to_dict()

    @property
    def _user_ytdl_options(self) -> Dict:
        return self._preset.ytdl_options.dict

    def builder(self) -> YTDLOptionsBuilder:
        """
        Returns
        -------
        YTDLOptionsBuilder
            Builder with values set based on the subscription
        """
        ytdl_options_builder = YTDLOptionsBuilder().add(self._global_options)
        if self._dry_run:
            ytdl_options_builder.add(
                self._subtitle_options, self._user_ytdl_options, self._dry_run_options
            )
        else:
            ytdl_options_builder.add(
                self._output_options,
                self._subtitle_options,
                self._audio_extract_options,
                self._user_ytdl_options,
            )

        return ytdl_options_builder
