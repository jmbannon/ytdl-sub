import contextlib
import logging
import os
import shutil
from abc import ABC
from pathlib import Path
from typing import List
from typing import Optional

from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.plugin.plugin import SplitPlugin
from ytdl_sub.config.plugin.plugin_mapping import PluginMapping
from ytdl_sub.config.plugin.plugin_operation import PluginOperation
from ytdl_sub.downloaders.info_json.info_json_downloader import InfoJsonDownloader
from ytdl_sub.downloaders.info_json.info_json_downloader import InfoJsonDownloaderOptions
from ytdl_sub.downloaders.source_plugin import SourcePlugin
from ytdl_sub.downloaders.url.downloader import MultiUrlDownloader
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.subscriptions.base_subscription import BaseSubscription
from ytdl_sub.subscriptions.subscription_ytdl_options import SubscriptionYTDLOptions
from ytdl_sub.utils.datetime import to_date_range
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger

logger: logging.Logger = Logger.get()


def _get_split_plugin(plugins: List[Plugin]) -> Optional[SplitPlugin]:
    split_plugins = [plugin for plugin in plugins if isinstance(plugin, SplitPlugin)]

    if len(split_plugins) == 1:
        return split_plugins[0]
    if len(split_plugins) > 1:
        raise ValidationException("Can not use more than one split plugins at a time")
    return None


class SubscriptionDownload(BaseSubscription, ABC):
    """
    Handles the subscription download logic
    """

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
        self.download_archive.save_file_to_output_directory(
            file_name=entry.get_download_file_name(),
            file_metadata=entry_metadata,
            output_file_name=output_file_name,
            entry=entry,
        )

        # Always pretend to include the thumbnail in a dry-run
        if self.output_options.thumbnail_name and (dry_run or entry.is_thumbnail_downloaded()):
            output_thumbnail_name = self.overrides.apply_formatter(
                formatter=self.output_options.thumbnail_name, entry=entry
            )

            # Copy the thumbnails since they could be used later for other things
            self.download_archive.save_file_to_output_directory(
                file_name=entry.get_download_thumbnail_name(),
                output_file_name=output_thumbnail_name,
                entry=entry,
                copy_file=True,
            )
        elif not entry.is_thumbnail_downloaded():
            logger.warning(
                "Cannot save thumbnail for '%s' because it is not available", entry.title
            )

        if self.output_options.info_json_name:
            output_info_json_name = self.overrides.apply_formatter(
                formatter=self.output_options.info_json_name, entry=entry
            )

            # if not dry-run, write the info json
            if not dry_run:
                entry.write_info_json()

            self.download_archive.save_file_to_output_directory(
                file_name=entry.get_download_info_json_name(),
                output_file_name=output_info_json_name,
                entry=entry,
            )

    def _delete_working_directory(self, is_error: bool = False) -> None:
        _ = is_error
        if os.path.isdir(self.working_directory):
            shutil.rmtree(self.working_directory)

    @contextlib.contextmanager
    def _prepare_working_directory(self):
        """
        Context manager to create all directories to the working directory. Deletes the entire
        working directory when cleaning up.
        """
        self._delete_working_directory()
        os.makedirs(self.working_directory, exist_ok=True)

        try:
            yield
        except Exception as exc:
            self._delete_working_directory(is_error=True)
            raise exc

        self._delete_working_directory()

    @contextlib.contextmanager
    def _maintain_archive_file(self):
        """
        Context manager to initialize the enhanced download archive
        """
        if self.maintain_download_archive:
            self.download_archive.prepare_download_archive()

        yield

        # If output options maintains stale file deletion, perform the delete here prior to saving
        # the download archive
        if self.maintain_download_archive:
            date_range_to_keep = to_date_range(
                before=self.output_options.keep_files_before,
                after=self.output_options.keep_files_after,
                overrides=self.overrides,
            )

            keep_max_files: Optional[int] = None
            if self.output_options.keep_max_files:
                # validated it can be cast to int within the validator
                keep_max_files = int(
                    self.overrides.apply_formatter(self.output_options.keep_max_files)
                )

            if date_range_to_keep or self.output_options.keep_max_files is not None:
                self.download_archive.remove_stale_files(
                    date_range=date_range_to_keep, keep_max_files=keep_max_files
                )

            self.download_archive.save_download_mappings()
            FileHandler.delete(self.download_archive.working_ytdl_file_path)

    @contextlib.contextmanager
    def _remove_empty_directories_in_output_directory(self):
        try:
            yield
        finally:
            if not self.download_archive.is_dry_run:
                for root, dir_names, _ in os.walk(Path(self.output_directory), topdown=False):
                    for dir_name in dir_names:
                        dir_path = Path(root) / dir_name
                        if len(os.listdir(dir_path)) == 0:
                            os.rmdir(dir_path)

    @contextlib.contextmanager
    def _subscription_download_context_managers(self) -> None:
        with (
            self._prepare_working_directory(),
            self._maintain_archive_file(),
            self._remove_empty_directories_in_output_directory(),
        ):
            yield

    def _initialize_plugins(self) -> List[Plugin]:
        """
        Returns
        -------
        List of plugins defined in the subscription, initialized and ready to use.
        """
        plugins = [
            plugin_type(
                options=plugin_options,
                overrides=self.overrides,
                enhanced_download_archive=self.download_archive,
            )
            for plugin_type, plugin_options in self.plugins.zipped()
        ]
        return [plugin for plugin in plugins if plugin.is_enabled]

    @classmethod
    def _cleanup_entry_files(cls, entry: Entry):
        FileHandler.delete(entry.get_download_file_path())
        FileHandler.delete(entry.get_download_thumbnail_path())
        FileHandler.delete(entry.get_download_info_json_path())

    @classmethod
    def _preprocess_entry(cls, plugins: List[Plugin], entry: Entry) -> Optional[Entry]:
        maybe_entry: Optional[Entry] = entry
        for plugin in PluginMapping.order_plugins_by(
            plugins, PluginOperation.MODIFY_ENTRY_METADATA
        ):
            if (maybe_entry := plugin.modify_entry_metadata(maybe_entry)) is None:
                return None

        return maybe_entry

    def _post_process_entry(
        self, plugins: List[Plugin], dry_run: bool, entry: Entry, entry_metadata: FileMetadata
    ):
        # Post-process the entry with all plugins
        for plugin in PluginMapping.order_plugins_by(plugins, PluginOperation.POST_PROCESS):
            optional_plugin_entry_metadata = plugin.post_process_entry(entry)
            if optional_plugin_entry_metadata:
                entry_metadata.extend(optional_plugin_entry_metadata)

        # Then, move it to the output directory
        self._move_entry_files_to_output_directory(
            dry_run=dry_run, entry=entry, entry_metadata=entry_metadata
        )

        # Re-save the download archive after each entry is moved to the output directory
        if self.maintain_download_archive:
            self.download_archive.save_download_mappings()

    def _process_entry(
        self, plugins: List[Plugin], dry_run: bool, entry: Entry, entry_metadata: FileMetadata
    ) -> None:
        entry_: Optional[Entry] = entry

        # First, modify the entry with all plugins
        for plugin in PluginMapping.order_plugins_by(plugins, PluginOperation.MODIFY_ENTRY):
            # Break if it is None, it is indicated to not process any further
            if (entry_ := plugin.modify_entry(entry_)) is None:
                break

        if entry_:
            self._post_process_entry(
                plugins=plugins, dry_run=dry_run, entry=entry_, entry_metadata=entry_metadata
            )

        self._cleanup_entry_files(entry)

    def _process_split_entry(
        self, split_plugin: SplitPlugin, plugins: List[Plugin], dry_run: bool, entry: Entry
    ) -> None:
        entry_: Optional[Entry] = entry

        # First, modify the entry with pre_split plugins
        for plugin in PluginMapping.order_plugins_by(
            plugins, PluginOperation.MODIFY_ENTRY, before_split=True
        ):
            # Break if it is None, it is indicated to not process any further
            if (entry_ := plugin.modify_entry(entry_)) is None:
                break

        # Then, perform the split
        if entry_:
            for split_entry, split_entry_metadata in split_plugin.split(entry=entry_):
                split_entry_: Optional[Entry] = split_entry

                for plugin in PluginMapping.order_plugins_by(
                    plugins, PluginOperation.MODIFY_ENTRY, before_split=False
                ):
                    # Return if it is None, it is indicated to not process any further.
                    # Break out of the plugin loop
                    if (split_entry_ := plugin.modify_entry(split_entry_)) is None:
                        break

                # If split_entry is None from modify_entry, do not post process
                if split_entry_:
                    self._post_process_entry(
                        plugins=plugins,
                        dry_run=dry_run,
                        entry=split_entry_,
                        entry_metadata=split_entry_metadata,
                    )

                self._cleanup_entry_files(split_entry)

        self._cleanup_entry_files(entry)

    def _process_subscription(
        self,
        plugins: List[Plugin],
        downloader: SourcePlugin,
        dry_run: bool,
    ) -> FileHandlerTransactionLog:
        with self._subscription_download_context_managers():
            for entry in downloader.download_metadata():
                if (entry := self._preprocess_entry(plugins=plugins, entry=entry)) is None:
                    continue

                entry = downloader.download(entry)
                if entry is None:
                    continue

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

        for plugin in plugins:
            plugin.post_process_subscription()

        return self.download_archive.get_file_handler_transaction_log()

    def download(self, dry_run: bool = False) -> FileHandlerTransactionLog:
        """
        Performs the subscription download

        Parameters
        ----------
        dry_run
            If true, do not download any video/audio files or move anything to the output
            directory.
        """
        self._exception = None
        self.download_archive.reinitialize(dry_run=dry_run)

        plugins = self._initialize_plugins()

        subscription_ytdl_options = SubscriptionYTDLOptions(
            preset=self._preset_options,
            plugins=plugins,
            enhanced_download_archive=self.download_archive,
            overrides=self.overrides,
            working_directory=self.working_directory,
            dry_run=dry_run,
        )

        downloader = MultiUrlDownloader(
            options=self.downloader_options,
            enhanced_download_archive=self.download_archive,
            download_ytdl_options=subscription_ytdl_options.download_builder(),
            metadata_ytdl_options=subscription_ytdl_options.metadata_builder(),
            overrides=self.overrides,
        )

        plugins.extend(downloader.added_plugins())

        return self._process_subscription(
            plugins=plugins,
            downloader=downloader,
            dry_run=dry_run,
        )

    @contextlib.contextmanager
    def exception_handling(self) -> None:
        """
        Try to perform something on the subscription.
        Store the error if one occurs.
        """
        try:
            yield
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("The following error occurred for the subscription %s:", self.name)
            self._exception = exc

        return self.transaction_log

    def update_with_info_json(self, dry_run: bool = False) -> FileHandlerTransactionLog:
        """
        Performs the subscription update using local info json files.

        Parameters
        ----------
        dry_run
            If true, do not modify any video/audio files or move anything to the output directory.
        """
        self._exception = None
        self.download_archive.reinitialize(dry_run=dry_run)

        plugins = self._initialize_plugins()

        subscription_ytdl_options = SubscriptionYTDLOptions(
            preset=self._preset_options,
            plugins=plugins,
            enhanced_download_archive=self.download_archive,
            overrides=self.overrides,
            working_directory=self.working_directory,
            dry_run=dry_run,
        )

        # Re-add the original downloader class' plugins
        plugins.extend(
            MultiUrlDownloader(
                options=self.downloader_options,
                enhanced_download_archive=self.download_archive,
                download_ytdl_options=subscription_ytdl_options.download_builder(),
                metadata_ytdl_options=subscription_ytdl_options.metadata_builder(),
                overrides=self.overrides,
            ).added_plugins()
        )

        downloader = InfoJsonDownloader(
            options=InfoJsonDownloaderOptions(name="no-op", value={}),
            enhanced_download_archive=self.download_archive,
            download_ytdl_options=YTDLOptionsBuilder(),
            metadata_ytdl_options=YTDLOptionsBuilder(),
            overrides=self.overrides,
        )

        return self._process_subscription(
            plugins=plugins,
            downloader=downloader,
            dry_run=dry_run,
        )
