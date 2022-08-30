import contextlib
import os
import shutil
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from ytdl_sub.config.config_file import ConfigFile
from ytdl_sub.config.config_file import ConfigOptions
from ytdl_sub.config.preset import Preset
from ytdl_sub.config.preset import PresetPlugins
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.config.preset_options import YTDLOptions
from ytdl_sub.downloaders.downloader import Downloader
from ytdl_sub.downloaders.downloader import DownloaderValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.subscriptions.subscription_ytdl_options import SubscriptionYTDLOptions
from ytdl_sub.utils.datetime import to_date_range
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.thumbnail import convert_download_thumbnail
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


def _get_split_plugin(plugins: List[Plugin]) -> Optional[Plugin]:
    split_plugins = [plugin for plugin in plugins if plugin.is_split_plugin]

    if len(split_plugins) == 1:
        return split_plugins[0]
    if len(split_plugins) > 1:
        raise ValidationException("Can not use more than one split plugins at a time")
    return None


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
    def plugins(self) -> PresetPlugins:
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

    def _move_entry_files_to_output_directory(
        self,
        dry_run: bool,
        entry: Entry,
        entry_metadata: Optional[FileMetadata] = None,
    ):
        """
        Helper function to move the media file and optionally thumbnail file to the output directory
        for a single entry.

        Parameters
        ----------
        dry_run
            Whether this session is a dry-run or not
        entry:
            The entry with files to move
        entry_metadata
            Optional. Metadata to record to the transaction log for this entry
        """
        # Move the file after all direct file modifications are complete
        output_file_name = self.overrides.apply_formatter(
            formatter=self.output_options.file_name, entry=entry
        )
        self._enhanced_download_archive.save_file_to_output_directory(
            file_name=entry.get_download_file_name(),
            file_metadata=entry_metadata,
            output_file_name=output_file_name,
            entry=entry,
        )

        # TODO: see if entry even has a thumbnail
        if self.output_options.thumbnail_name:
            output_thumbnail_name = self.overrides.apply_formatter(
                formatter=self.output_options.thumbnail_name, entry=entry
            )

            # We always convert entry thumbnails to jpgs, and is performed here
            if not dry_run:
                convert_download_thumbnail(entry=entry)

            self._enhanced_download_archive.save_file_to_output_directory(
                file_name=entry.get_download_thumbnail_name(),
                output_file_name=output_thumbnail_name,
                entry=entry,
            )

        if self.output_options.info_json_name:
            output_info_json_name = self.overrides.apply_formatter(
                formatter=self.output_options.info_json_name, entry=entry
            )

            # if not dry-run, write the info json
            if not dry_run:
                entry.write_info_json()

            self._enhanced_download_archive.save_file_to_output_directory(
                file_name=entry.get_download_info_json_name(),
                output_file_name=output_info_json_name,
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
            date_range_to_keep = to_date_range(
                before=self.output_options.keep_files_before,
                after=self.output_options.keep_files_after,
                overrides=self.overrides,
            )
            if date_range_to_keep:
                self._enhanced_download_archive.remove_stale_files(date_range=date_range_to_keep)

            self._enhanced_download_archive.save_download_mappings()

    @contextlib.contextmanager
    def _subscription_download_context_managers(self) -> None:
        with (
            self._prepare_working_directory(),
            self._maintain_archive_file(),
        ):
            yield

    def _initialize_plugins(self) -> List[Plugin]:
        """
        Returns
        -------
        List of plugins defined in the subscription, initialized and ready to use.
        """
        plugins: List[Plugin] = []
        for plugin_type, plugin_options in self.plugins.zipped():
            plugin = plugin_type(
                plugin_options=plugin_options,
                overrides=self.overrides,
                enhanced_download_archive=self._enhanced_download_archive,
            )

            plugins.append(plugin)

        return plugins

    def _post_process_entry(
        self, plugins: List[Plugin], dry_run: bool, entry: Entry, entry_metadata: FileMetadata
    ):
        # Post-process the entry with all plugins
        for plugin in sorted(plugins, key=lambda _plugin: _plugin.priority.post_process):
            optional_plugin_entry_metadata = plugin.post_process_entry(entry)
            if optional_plugin_entry_metadata:
                entry_metadata.extend(optional_plugin_entry_metadata)

        # Then, move it to the output directory
        self._move_entry_files_to_output_directory(
            dry_run=dry_run, entry=entry, entry_metadata=entry_metadata
        )

        # Re-save the download archive after each entry is moved to the output directory
        if self.maintain_download_archive:
            self._enhanced_download_archive.save_download_mappings()

    def _process_entry(
        self, plugins: List[Plugin], dry_run: bool, entry: Entry, entry_metadata: FileMetadata
    ) -> None:
        # First, modify the entry with all plugins
        for plugin in sorted(plugins, key=lambda _plugin: _plugin.priority.modify_entry):
            # Return if it is None, it is indicated to not process any further
            if (entry := plugin.modify_entry(entry)) is None:
                return

        self._post_process_entry(
            plugins=plugins, dry_run=dry_run, entry=entry, entry_metadata=entry_metadata
        )

    def _process_split_entry(
        self, split_plugin: Plugin, plugins: List[Plugin], dry_run: bool, entry: Entry
    ) -> None:
        plugins_pre_split = sorted(
            [plugin for plugin in plugins if not plugin.priority.modify_entry_after_split],
            key=lambda _plugin: _plugin.priority.modify_entry,
        )

        plugins_post_split = sorted(
            [plugin for plugin in plugins if plugin.priority.modify_entry_after_split],
            key=lambda _plugin: _plugin.priority.modify_entry,
        )

        # First, modify the entry with pre_split plugins
        for plugin in plugins_pre_split:
            # Return if it is None, it is indicated to not process any further
            if (entry := plugin.modify_entry(entry)) is None:
                return

        # Then, perform the split
        for split_entry, split_entry_metadata in split_plugin.split(entry=entry):

            for plugin in plugins_post_split:
                # Return if it is None, it is indicated to not process any further.
                # Break out of the plugin loop
                if (split_entry := plugin.modify_entry(split_entry)) is None:
                    break

            # If split_entry is None from modify_entry, do not post process
            if split_entry:
                self._process_entry(
                    plugins=plugins,
                    dry_run=dry_run,
                    entry=split_entry,
                    entry_metadata=split_entry_metadata,
                )

    def download(self, dry_run: bool = False) -> FileHandlerTransactionLog:
        """
        Performs the subscription download

        Parameters
        ----------
        dry_run
            If true, do not download any video/audio files or move anything to the output
            directory.
        """
        self._enhanced_download_archive.reinitialize(dry_run=dry_run)
        plugins = self._initialize_plugins()

        ytdl_options_builder = SubscriptionYTDLOptions(
            preset=self.__preset_options,
            plugins=plugins,
            enhanced_download_archive=self._enhanced_download_archive,
            working_directory=self.working_directory,
            dry_run=dry_run,
        ).builder()

        with self._subscription_download_context_managers():
            downloader = self.downloader_class(
                download_options=self.downloader_options,
                enhanced_download_archive=self._enhanced_download_archive,
                ytdl_options_builder=ytdl_options_builder,
            )

            for entry in downloader.download():
                entry_metadata = FileMetadata()
                if isinstance(entry, tuple):
                    entry, entry_metadata = entry

                if split_plugin := _get_split_plugin(plugins):
                    self._process_split_entry(
                        split_plugin=split_plugin, plugins=plugins, dry_run=dry_run, entry=entry
                    )
                else:
                    self._process_entry(
                        plugins=plugins, dry_run=dry_run, entry=entry, entry_metadata=entry_metadata
                    )

            downloader.post_download(overrides=self.overrides)
            for plugin in plugins:
                plugin.post_process_subscription()

        return self._enhanced_download_archive.get_file_handler_transaction_log()

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

    @classmethod
    def from_dict(cls, config: ConfigFile, preset_name: str, preset_dict: Dict) -> "Subscription":
        """
        Creates a subscription from a preset dict

        Parameters
        ----------
        config:
            Validated instance of the config
        preset_name:
            Name of the preset
        preset_dict:
            The preset config in dict format

        Returns
        -------
        Initialized subscription
        """
        return cls.from_preset(
            preset=Preset.from_dict(
                config=config,
                preset_name=preset_name,
                preset_dict=preset_dict,
            ),
            config=config,
        )
