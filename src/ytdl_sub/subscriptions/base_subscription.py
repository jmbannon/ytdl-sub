from abc import ABC
from pathlib import Path
from typing import Optional

from ytdl_sub.config.config_validator import ConfigOptions
from ytdl_sub.config.preset import Preset
from ytdl_sub.config.preset import PresetPlugins
from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.config.preset_options import YTDLOptions
from ytdl_sub.downloaders.url.validators import MultiUrlValidator
from ytdl_sub.utils.logger import Logger
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

logger = Logger.get("subscription")


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

        migrated_file_name: Optional[str] = None
        if migrated_file_name_option := self.output_options.migrated_download_archive_name:
            migrated_file_name = self.overrides.apply_formatter(migrated_file_name_option)

        # TODO: Do not include this as part of the subscription
        self._enhanced_download_archive = EnhancedDownloadArchive(
            file_name=self.overrides.apply_formatter(self.output_options.download_archive_name),
            working_directory=self.working_directory,
            output_directory=self.output_directory,
            migrated_file_name=migrated_file_name,
        )

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
        return self._enhanced_download_archive.num_entries_added

    @property
    def num_entries_modified(self) -> int:
        """
        Returns
        -------
        Number of entries modified
        """
        return self._enhanced_download_archive.num_entries_modified

    @property
    def num_entries_removed(self) -> int:
        """
        Returns
        -------
        Number of entries removed
        """
        return self._enhanced_download_archive.num_entries_removed

    @property
    def num_entries(self) -> int:
        """
        Returns
        -------
        The number of entries
        """
        return self._enhanced_download_archive.num_entries

    def as_yaml(self) -> str:
        """
        Returns
        -------
        Subscription in yaml format
        """
        return self._preset_options.yaml
