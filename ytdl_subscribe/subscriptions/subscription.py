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

import dicttoxml
import music_tag
from PIL import Image

from ytdl_subscribe.downloaders.downloader import Downloader
from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.validators.base.string_formatter_validators import StringFormatterValidator
from ytdl_subscribe.validators.config.config_options.config_options_validator import (
    ConfigOptionsValidator,
)
from ytdl_subscribe.validators.config.metadata_options.metadata_options_validator import (
    MetadataOptionsValidator,
)
from ytdl_subscribe.validators.config.metadata_options.nfo_validator import NFOValidator
from ytdl_subscribe.validators.config.output_options.output_options_validator import (
    OutputOptionsValidator,
)
from ytdl_subscribe.validators.config.overrides.overrides_validator import OverridesValidator
from ytdl_subscribe.validators.config.preset_validator import PresetValidator
from ytdl_subscribe.validators.config.source_options.mixins import DownloadDateRangeSource
from ytdl_subscribe.validators.config.source_options.source_validators import SourceValidator
from ytdl_subscribe.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

SourceT = TypeVar("SourceT", bound=SourceValidator)
EntryT = TypeVar("EntryT", bound=Entry)
DownloaderT = TypeVar("DownloaderT", bound=Downloader)


class Subscription(Generic[SourceT], ABC):
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
        entry_type: Type[EntryT],
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
        self.__entry_type = entry_type

        self._enhanced_download_archive = EnhancedDownloadArchive(
            subscription_name=name,
            working_directory=self.working_directory,
            output_directory=self.output_directory,
        )

    @property
    def entry_type(self) -> EntryT:
        """
        :return: The Entry type this subscription uses to represent downloaded media
        """
        return self.__entry_type

    @property
    def source_options(self) -> SourceT:
        """Returns the source options defined for this subscription"""
        return self.__preset_options.subscription_source

    @property
    def output_options(self) -> OutputOptionsValidator:
        """Returns the output options defined for this subscription"""
        return self.__preset_options.output_options

    @property
    def metadata_options(self) -> MetadataOptionsValidator:
        """Returns the metadata options defined for this subscription"""
        return self.__preset_options.metadata_options

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
        return self._apply_formatter(formatter=self.output_options.output_directory)

    def _archive_entry_file_name(self, entry: Optional[Entry], relative_file_name: str) -> None:
        """
        Adds an entry and a file name that belongs to it into the archive mapping.

        :param entry: Optional. The entry the file belongs to
        :param relative_file_name: The name of the file
        """
        if entry:
            self._enhanced_download_archive.mapping.add_entry(
                entry=entry, entry_file_path=relative_file_name
            )

    def get_downloader(
        self, downloader_type: Type[DownloaderT], source_ytdl_options: Optional[Dict] = None
    ) -> DownloaderT:
        """Returns the downloader that will be used to download media for this subscription"""
        # if source_ytdl_options are present, override the ytdl_options with them
        ytdl_options = self.__preset_options.ytdl_options.dict
        if source_ytdl_options:
            ytdl_options = dict(ytdl_options, **source_ytdl_options)

        return downloader_type(
            output_directory=self.working_directory,
            ytdl_options=ytdl_options,
            download_archive_file_name=self._enhanced_download_archive.archive_file_name,
        )

    def _apply_formatter(
        self, formatter: StringFormatterValidator, entry: Optional[Entry] = None
    ) -> str:
        """
        Returns the format_string after .format has been called on it using entry (if provided) and
        override values
        """
        variable_dict = self.overrides.dict_with_format_strings
        if entry:
            variable_dict = dict(entry.to_dict(), **variable_dict)
        return formatter.apply_formatter(variable_dict)

    def _post_process_tagging(self, entry: Entry):
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        id3_options = self.metadata_options.id3
        entry_source_file_path = Path(self.working_directory) / entry.download_file_name

        audio_file = music_tag.load_file(entry_source_file_path)
        for tag, tag_formatter in id3_options.tags.dict.items():
            audio_file[tag] = self._apply_formatter(formatter=tag_formatter, entry=entry)
        audio_file.save()

    def _post_process_nfo(self, nfo_options: NFOValidator, entry: Optional[Entry] = None):
        """
        Creates an entry's NFO file using values defined in the metadata options

        :param nfo_options: Options for the NFO
        :param entry: Optional. Will pass entry values to nfo string formatters. If None, will only
        use override variables that must resolve.
        """
        nfo = {}

        for tag, tag_formatter in nfo_options.tags.dict.items():
            nfo[tag] = self._apply_formatter(formatter=tag_formatter, entry=entry)

        # Write the nfo tags to XML with the nfo_root
        nfo_root = self._apply_formatter(formatter=nfo_options.nfo_root, entry=entry)
        xml = dicttoxml.dicttoxml(
            obj=nfo,
            root=True,  # We assume all NFOs have a root. Maybe we should not?
            custom_root=nfo_root,
            attr_type=False,
        )

        nfo_file_name = self._apply_formatter(formatter=nfo_options.nfo_name, entry=entry)

        # Save the nfo's XML to file
        nfo_file_path = Path(self.output_directory) / Path(nfo_file_name)
        with open(nfo_file_path, "wb") as nfo_file:
            nfo_file.write(xml)

        # Archive the nfo's file name
        self._archive_entry_file_name(entry=entry, relative_file_name=nfo_file_name)

    def _post_process_thumbnail(self, entry: Entry):
        source_thumbnail_path = Path(self.working_directory) / entry.download_thumbnail_name

        # Bug that mismatches webp and jpg extensions. Try to hotfix here
        if not os.path.isfile(source_thumbnail_path):
            to_replace = f".{entry.thumbnail_ext}"
            actual_thumbnail_ext = ".webp"
            if entry.thumbnail_ext == "webp":
                actual_thumbnail_ext = ".jpg"

            source_thumbnail_name = entry.download_thumbnail_name.replace(
                to_replace, actual_thumbnail_ext
            )
            source_thumbnail_path = Path(self.working_directory) / source_thumbnail_name

            if not os.path.isfile(source_thumbnail_path):
                raise ValueError("Hotfix for getting thumbnail file extension failed")

        output_thumbnail_name = self._apply_formatter(
            formatter=self.output_options.thumbnail_name, entry=entry
        )
        output_thumbnail_path = Path(self.output_directory) / Path(output_thumbnail_name)

        os.makedirs(os.path.dirname(output_thumbnail_path), exist_ok=True)

        # If the thumbnail is to be converted, then save the converted thumbnail to the
        # output filepath
        if self.output_options.convert_thumbnail:
            image = Image.open(source_thumbnail_path).convert("RGB")
            image.save(
                fp=output_thumbnail_path,
                format=self.output_options.convert_thumbnail.value,
            )
        # Otherwise, just copy the downloaded thumbnail
        else:
            copyfile(source_thumbnail_path, output_thumbnail_path)

        # Archive the thumbnail file name
        self._archive_entry_file_name(entry=entry, relative_file_name=output_thumbnail_name)

    def _copy_entry_file_to_output_directory(self, entry: Entry):
        # Move the file after all direct file modifications are complete
        entry_source_file_path = Path(self.working_directory) / entry.download_file_name

        output_file_name = self._apply_formatter(
            formatter=self.output_options.file_name, entry=entry
        )
        entry_destination_file_path = Path(self.output_directory) / Path(output_file_name)

        os.makedirs(os.path.dirname(entry_destination_file_path), exist_ok=True)
        copyfile(entry_source_file_path, entry_destination_file_path)

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
            - Adding metadata to the entry file itself (music tags)
            - Moving the entry file + thumbnail to the output directory with its formatted name
            - Creating new metadata files (NFO) to reside alongside the entry files

        :param entry: The entry to post-process
        """
        if self.metadata_options.id3:
            self._post_process_tagging(entry)

        self._copy_entry_file_to_output_directory(entry=entry)

        if self.output_options.thumbnail_name:
            self._post_process_thumbnail(entry=entry)

        if self.metadata_options.nfo:
            self._post_process_nfo(nfo_options=self.metadata_options.nfo, entry=entry)

        if self.metadata_options.output_directory_nfo:
            self._post_process_nfo(nfo_options=self.metadata_options.output_directory_nfo)
