import contextlib
import copy
import os
import shutil
from pathlib import Path
from typing import List
from typing import Tuple
from typing import Type

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.config_file import ConfigOptions
from ytdl_sub.config.preset import Preset
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.config.preset_options import YTDLOptions
from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.thumbnail import convert_download_thumbnail
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class Subscription:
    """
    Subscription classes are the 'controllers' that perform...

    -  Downloading via ytdlp
    -  Adding metadata
    -  Placing files in the output directory

    while configuring each step with provided configs. Child classes are expected to
    provide SourceValidator (SourceT), which defines the source and its configurable options.
    In addition, they should provide in the init an Entry type (EntryT), which is the entry that
    will be returned after downloading.
    """

    def __init__(
        self,
        name: str,
        config_options: ConfigOptions,
        preset_options: Preset,
    ):
        """
        Parameters
        ----------
        name: str
            Name of the subscription
        config_options: ConfigOptions
        preset_options: Preset
        """
        self.name = name
        self.__config_options = config_options
        self.__preset_options = preset_options

        self._enhanced_download_archive = EnhancedDownloadArchive(
            subscription_name=name,
            working_directory=self.working_directory,
            output_directory=self.output_directory,
        )

    @property
    def downloader_class(self) -> Type[Downloader]:
        """
        Returns
        -------
        This subscription's downloader class
        """
        return self.__preset_options.downloader

    @property
    def downloader_options(self) -> DownloaderValidator:
        """
        Returns
        -------
        The download options for this subscription's downloader
        """
        return self.__preset_options.downloader_options

    @property
    def plugins(self) -> List[Tuple[Type[Plugin], PluginOptions]]:
        """
        Returns
        -------
        List of tuples containing (plugin class, plugin options)
        """
        return self.__preset_options.plugins

    @property
    def ytdl_options(self) -> YTDLOptions:
        """
        Returns
        -------
        YTDL options for this subscription
        """
        return self.__preset_options.ytdl_options

    @property
    def output_options(self) -> OutputOptions:
        """
        Returns
        -------
        The output options defined for this subscription
        """
        return self.__preset_options.output_options

    @property
    def overrides(self) -> Overrides:
        """
        Returns
        -------
        The overrides defined for this subscription
        """
        return self.__preset_options.overrides

    @property
    def working_directory(self) -> str:
        """
        Returns
        -------
        The directory that the downloader saves files to
        """
        return str(Path(self.__config_options.working_directory) / Path(self.name))

    @property
    def output_directory(self) -> str:
        """
        Returns
        -------
        The formatted output directory
        """
        return self.overrides.apply_formatter(formatter=self.output_options.output_directory)

    @property
    def maintain_download_archive(self) -> bool:
        """
        Returns
        -------
        Whether to maintain a download archive
        """
        return (
            self.output_options.maintain_download_archive
            and self.downloader_class.supports_download_archive
        )

    def _copy_entry_files_to_output_directory(self, entry: Entry):
        """
        Helper function to move the media file and optionally thumbnail file to the output directory
        for a single entry.

        Parameters
        ----------
        entry:
            The entry with files to move
        """
        # Move the file after all direct file modifications are complete
        output_file_name = self.overrides.apply_formatter(
            formatter=self.output_options.file_name, entry=entry
        )
        self._enhanced_download_archive.save_file(
            file_name=entry.get_download_file_path(), output_file_name=output_file_name, entry=entry
        )

        if self.output_options.thumbnail_name:
            output_thumbnail_name = self.overrides.apply_formatter(
                formatter=self.output_options.thumbnail_name, entry=entry
            )

            # We always convert entry thumbnails to jpgs, and is performed here
            convert_download_thumbnail(entry=entry)

            self._enhanced_download_archive.save_file(
                file_name=entry.get_download_file_name(),
                output_file_name=output_thumbnail_name,
                entry=entry,
            )

    @contextlib.contextmanager
    def _prepare_working_directory(self):
        """
        Context manager to create all directories to the working directory. Deletes the entire
        working directory when cleaning up.
        """
        os.makedirs(self.working_directory, exist_ok=True)

        try:
            yield
        finally:
            shutil.rmtree(self.working_directory)

    @contextlib.contextmanager
    def _maintain_archive_file(self):
        """
        Context manager to initialize the enhanced download archive
        """
        if self.maintain_download_archive:
            self._enhanced_download_archive.prepare_download_archive()

        yield

        # If output options maintains stale file deletion, perform the delete here prior to saving
        # the download archive
        if self.maintain_download_archive:
            date_range_to_keep = self.output_options.get_upload_date_range_to_keep()
            if date_range_to_keep:
                self._enhanced_download_archive.remove_stale_files(date_range=date_range_to_keep)

            self._enhanced_download_archive.save_download_mappings()

    def _initialize_plugins(self) -> List[Plugin]:
        """
        Returns
        -------
        List of plugins defined in the subscription, initialized and ready to use.
        """
        plugins: List[Plugin] = []
        for plugin_type, plugin_options in self.plugins:
            plugin = plugin_type(
                plugin_options=plugin_options,
                overrides=self.overrides,
                enhanced_download_archive=self._enhanced_download_archive,
            )

            plugins.append(plugin)

        return plugins

    def download(self, dry_run: bool = False):
        """
        Performs the subscription download

        Parameters
        ----------
        dry_run
            If true, do not download any video/audio files or move anything to the output
            directory.
        """
        # TODO: Move this logic to separate function
        # TODO: set id here as well
        ytdl_options = copy.deepcopy(self.ytdl_options.dict)
        if dry_run:
            ytdl_options["skip_download"] = True
        if self.downloader_class.supports_download_archive and self.maintain_download_archive:
            ytdl_options["download_archive"] = str(
                Path(self.working_directory) / self._enhanced_download_archive.archive_file_name
            )

        plugins = self._initialize_plugins()
        with self._prepare_working_directory(), self._maintain_archive_file():
            downloader = self.downloader_class(
                working_directory=self.working_directory,
                download_options=self.downloader_options,
                ytdl_options=ytdl_options,
            )

            entries = downloader.download()
            for plugin in plugins:
                for entry in entries:
                    plugin.post_process_entry(entry)

                plugin.post_process_subscription()

            for entry in entries:
                self._copy_entry_files_to_output_directory(entry=entry)

            downloader.post_download(
                overrides=self.overrides, output_directory=self.output_directory
            )

    @classmethod
    def from_preset(cls, preset: Preset, config: ConfigFile) -> "Subscription":
        """
        Creates a subscription from a preset

        Parameters
        ----------
        preset
            Preset to make the subscription out of
        config
            The config file that should contain this preset

        Returns
        -------
        Initialized subscription
        """
        return cls(
            name=preset.name,
            preset_options=preset,
            config_options=config.config_options,
        )
