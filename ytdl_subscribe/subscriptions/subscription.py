import contextlib
import os
import shutil
from abc import ABC
from pathlib import Path
from shutil import copyfile
from typing import Dict
from typing import Generic
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from ytdl_subscribe.config.config_options_validator import ConfigOptionsValidator
from ytdl_subscribe.config.output_options_validator import OutputOptionsValidator
from ytdl_subscribe.config.overrides_validator import OverridesValidator
from ytdl_subscribe.config.preset_validator import PresetValidator
from ytdl_subscribe.downloaders.downloader import Downloader
from ytdl_subscribe.downloaders.downloader import DownloaderValidator
from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.validators.date_range_validator import DownloadDateRangeSource
from ytdl_subscribe.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

SourceT = TypeVar("SourceT", bound=DownloaderValidator)
EntryT = TypeVar("EntryT", bound=Entry)
DownloaderT = TypeVar("DownloaderT", bound=Downloader)


class Subscription(Generic[SourceT, EntryT], ABC):
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
        config_options: ConfigOptionsValidator,
        preset_options: PresetValidator,
    ):
        """
        Parameters
        ----------
        name: str
            Name of the subscription
        config_options: ConfigOptionsValidator
        preset_options: PresetValidator
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
    def entry_type(self) -> Type[EntryT]:
        """
        :return: The Entry type this subscription uses to represent downloaded media
        """
        return EntryT.__class__

    @property
    def source_options(self) -> SourceT:
        """Returns the source options defined for this subscription"""
        return self.__preset_options.subscription_source

    @property
    def output_options(self) -> OutputOptionsValidator:
        """Returns the output options defined for this subscription"""
        return self.__preset_options.output_options

    @property
    def overrides(self) -> OverridesValidator:
        """Returns the overrides defined for this subscription"""
        return self.__preset_options.overrides

    @property
    def working_directory(self) -> str:
        """Returns the directory that the downloader saves files to"""
        return str(Path(self.__config_options.working_directory.value) / Path(self.name))

    @property
    def output_directory(self) -> str:
        """
        :return: The formatted output directory
        """
        return self.overrides.apply_formatter(formatter=self.output_options.output_directory)

    def get_downloader(
        self, downloader_type: Type[DownloaderT], source_ytdl_options: Optional[Dict] = None
    ) -> DownloaderT:
        """Returns the downloader that will be used to download media for this subscription"""
        # if source_ytdl_options are present, override the ytdl_options with them
        ytdl_options = self.__preset_options.ytdl_options.dict
        if source_ytdl_options:
            ytdl_options = dict(ytdl_options, **source_ytdl_options)

        return downloader_type(
            working_directory=self.working_directory,
            ytdl_options=ytdl_options,
            download_archive_file_name=self._enhanced_download_archive.archive_file_name,
        )

    def _copy_file_to_output_directory(self, source_file_path: str, output_file_name: str):
        destination_file_path = Path(self.output_directory) / Path(output_file_name)
        os.makedirs(os.path.dirname(destination_file_path), exist_ok=True)
        copyfile(source_file_path, destination_file_path)

    def _copy_entry_files_to_output_directory(self, entry: Entry):
        # Move the file after all direct file modifications are complete
        output_file_name = self.overrides.apply_formatter(
            formatter=self.output_options.file_name, entry=entry
        )
        self._enhanced_download_archive.mapping.add_entry(entry, output_file_name)
        self._copy_file_to_output_directory(
            source_file_path=entry.download_file_path, output_file_name=output_file_name
        )

        if self.output_options.thumbnail_name:
            output_thumbnail_name = self.overrides.apply_formatter(
                formatter=self.output_options.thumbnail_name, entry=entry
            )
            self._enhanced_download_archive.mapping.add_entry(entry, output_thumbnail_name)
            self._copy_file_to_output_directory(
                source_file_path=entry.download_thumbnail_path,
                output_file_name=output_thumbnail_name,
            )

        self._enhanced_download_archive.mapping.add_entry(entry, output_file_name)

    @contextlib.contextmanager
    def _prepare_working_directory(self):
        os.makedirs(self.working_directory, exist_ok=True)

        yield

        shutil.rmtree(self.working_directory)

    @contextlib.contextmanager
    def _maintain_archive_file(self):
        if not self.output_options.maintain_download_archive:
            return

        self._enhanced_download_archive.prepare_download_archive()

        yield

        date_range = None
        if isinstance(self.source_options, DownloadDateRangeSource):
            date_range = self.source_options.get_date_range()

        if date_range and self.output_options.maintain_stale_file_deletion:
            self._enhanced_download_archive.remove_stale_files(date_range=date_range)

        self._enhanced_download_archive.save_download_archive()

    def download(self):
        """
        Performs the subscription download.
        """
        with self._prepare_working_directory(), self._maintain_archive_file():
            entries = self._extract_info()
            for entry in entries:
                self.post_process_entry(entry)

    def _extract_info(self) -> List[EntryT]:
        """
        Extracts only the info of the source, does not download it
        """
        raise NotImplementedError("Each source needs to implement how it extracts info")

    def post_process_entry(self, entry: Entry) -> None:
        """
        After downloading an entry to the working directory, perform all post-processing, which
        includes:

        * Adding metadata to the entry file itself (music tags)
        * Moving the entry file + thumbnail to the output directory with its formatted name
        * Creating new metadata files (NFO) to reside alongside the entry files

        :param entry: The entry to post-process
        """
        # before move
        self._copy_entry_files_to_output_directory(entry=entry)

        # after move
