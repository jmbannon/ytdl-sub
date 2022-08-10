from pathlib import Path
from typing import Dict

from ytdl_sub.config.preset import Preset
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class SubscriptionYTDLOptions:
    def __init__(
        self,
        preset: Preset,
        enhanced_download_archive: EnhancedDownloadArchive,
        working_directory: str,
        dry_run: bool,
    ):
        self._preset = preset
        self._enhanced_download_archive = enhanced_download_archive
        self._working_directory = working_directory
        self._dry_run = dry_run

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
            self._preset.downloader.supports_download_archive
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
            "writesubtitles": False,
        }

    @property
    def _output_options(self) -> Dict:
        ytdl_options = {}
        output_options = self._preset.output_options

        if output_options.thumbnail_name:
            ytdl_options["writethumbnail"] = True

        return ytdl_options

    @property
    def _subtitle_options(self) -> Dict:
        ytdl_options: Dict = {}
        subtitle_options = self._preset.subtitle_options

        write_subtitle_file: bool = subtitle_options.subtitles_name is not None
        if write_subtitle_file:
            ytdl_options["writesubtitles"] = True
            ytdl_options["postprocessors"] = [
                {"key": "FFmpegSubtitlesConvertor", "format": subtitle_options.subtitles_type}
            ]

        if subtitle_options.embed_subtitles:
            ytdl_options["postprocessors"] = [
                # already_have_subtitle=True means keep the subtitle files. False means delete
                {"key": "FFmpegEmbedSubtitle", "already_have_subtitle": write_subtitle_file}
            ]

        # If neither subtitles_name or embed_subtitles is set, do not set any other flags
        if not ytdl_options:
            return {}

        ytdl_options["writeautomaticsub"] = subtitle_options.allow_auto_generated_subtitles
        ytdl_options["subtitleslangs"] = subtitle_options.languages

        return ytdl_options

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
            ytdl_options_builder.add(self._dry_run_options, self._user_ytdl_options)
        else:
            ytdl_options_builder.add(
                self._output_options, self._subtitle_options, self._user_ytdl_options
            )

        return ytdl_options_builder
