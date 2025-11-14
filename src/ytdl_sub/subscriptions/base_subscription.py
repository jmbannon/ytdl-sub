from abc import ABC
from pathlib import Path
from typing import Optional

from ytdl_sub.config.config_validator import ConfigOptions
from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.plugin.preset_plugins import PresetPlugins
from ytdl_sub.config.preset import Preset
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.preset_options import YTDLOptions
from ytdl_sub.downloaders.url.validators import MultiUrlValidator
from ytdl_sub.entries.variables.override_variables import SubscriptionVariables
from ytdl_sub.utils.file_handler import FileHandlerTransactionLog
from ytdl_sub.utils.logger import Logger
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

logger = Logger.get("subscription")


def _initialize_download_archive(
    output_options: OutputOptions,
    overrides: Overrides,
    working_directory: str,
    output_directory: str,
) -> EnhancedDownloadArchive:
    migrated_file_name: Optional[str] = None
    if migrated_file_name_option := output_options.migrated_download_archive_name:
        migrated_file_name = overrides.apply_formatter(migrated_file_name_option)

    return EnhancedDownloadArchive(
        file_name=overrides.apply_formatter(output_options.download_archive_name),
        working_directory=working_directory,
        output_directory=output_directory,
        migrated_file_name=migrated_file_name,
    ).reinitialize(dry_run=True)


class BaseSubscription(ABC):
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
        self._config_options = config_options
        self._preset_options = preset_options

        # Add overrides pre-archive
        self.overrides.add(
            {
                SubscriptionVariables.subscription_name(): self.name,
            }
        )

        self._enhanced_download_archive: Optional[EnhancedDownloadArchive] = (
            _initialize_download_archive(
                output_options=self.output_options,
                overrides=self.overrides,
                working_directory=self.working_directory,
                output_directory=self.output_directory,
            )
        )

        # Add post-archive variables
        self.overrides.add(
            {
                SubscriptionVariables.subscription_has_download_archive(): f"""{{
                        %bool({self.download_archive.num_entries > 0})
                    }}""",
            }
        )

        self._exception: Optional[Exception] = None

    @property
    def download_archive(self) -> EnhancedDownloadArchive:
        """
        Returns
        -------
        Initialized download archive
        """
        assert self._enhanced_download_archive is not None
        return self._enhanced_download_archive

    @property
    def downloader_options(self) -> MultiUrlValidator:
        """
        Returns
        -------
        The download options for this subscription's downloader
        """
        return self._preset_options.downloader_options

    @property
    def plugins(self) -> PresetPlugins:
        """
        Returns
        -------
        List of tuples containing (plugin class, plugin options)
        """
        return self._preset_options.plugins

    @property
    def ytdl_options(self) -> YTDLOptions:
        """
        Returns
        -------
        YTDL options for this subscription
        """
        return self._preset_options.ytdl_options

    @property
    def output_options(self) -> OutputOptions:
        """
        Returns
        -------
        The output options defined for this subscription
        """
        return self._preset_options.output_options

    @property
    def overrides(self) -> Overrides:
        """
        Returns
        -------
        The overrides defined for this subscription
        """
        return self._preset_options.overrides

    @property
    def working_directory(self) -> str:
        """
        Returns
        -------
        The directory that the downloader saves files to
        """
        return str(Path(self._config_options.working_directory) / Path(self.name))

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
        return self.output_options.maintain_download_archive

    @property
    def num_entries_added(self) -> int:
        """
        Returns
        -------
        Number of entries added
        """
        return self.download_archive.num_entries_added

    @property
    def num_entries_modified(self) -> int:
        """
        Returns
        -------
        Number of entries modified
        """
        return self.download_archive.num_entries_modified

    @property
    def num_entries_removed(self) -> int:
        """
        Returns
        -------
        Number of entries removed
        """
        return self.download_archive.num_entries_removed

    @property
    def num_entries(self) -> int:
        """
        Returns
        -------
        The number of entries
        """
        return self.download_archive.num_entries

    @property
    def transaction_log(self) -> FileHandlerTransactionLog:
        """
        Returns
        -------
        Transaction log from the subscription
        """
        return self.download_archive.get_file_handler_transaction_log()

    @property
    def exception(self) -> Optional[Exception]:
        """
        Returns
        -------
        An exception if one occurred while processing the subscription
        """
        return self._exception

    def as_yaml(self) -> str:
        """
        Returns
        -------
        Subscription in yaml format
        """
        return self._preset_options.yaml
