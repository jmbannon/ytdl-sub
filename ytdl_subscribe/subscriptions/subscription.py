import contextlib
import os
import shutil
from abc import ABC
from pathlib import Path
from shutil import copyfile
from typing import Dict
from typing import Generic
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

S = TypeVar("S", bound=SourceValidator)
D = TypeVar("D", bound=Downloader)


class Subscription(Generic[S], ABC):
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
    def source_options(self) -> S:
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
    def output_directory(self):
        return self._apply_formatter(formatter=self.output_options.output_directory)

    def _archive_entry_file_name(self, entry: Optional[Entry], relative_file_name: str) -> None:
        if entry:
            self._enhanced_download_archive.mapping.add_entry(
                entry=entry, entry_file_path=relative_file_name
            )

    def get_downloader(
        self, downloader_type: Type[D], source_ytdl_options: Optional[Dict] = None
    ) -> D:
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
        audio_file = music_tag.load_file(entry.file_path(relative_directory=self.working_directory))
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
        output_directory = self._apply_formatter(
            formatter=self.output_options.output_directory, entry=entry
        )

        # Save the nfo's XML to file
        nfo_file_path = Path(output_directory) / Path(nfo_file_name)
        with open(nfo_file_path, "wb") as nfo_file:
            nfo_file.write(xml)

        # Archive the nfo's file name
        self._archive_entry_file_name(entry=entry, relative_file_name=nfo_file_name)

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
        with self._maintain_archive_file():
            self._extract_info()

    def _extract_info(self):
        """
        Extracts only the info of the source, does not download it
        """
        raise NotImplementedError("Each source needs to implement how it extracts info")

    def post_process_entry(self, entry: Entry):
        if self.metadata_options.id3:
            self._post_process_tagging(entry)

        # Move the file after all direct file modifications are complete
        entry_source_file_path = entry.file_path(relative_directory=self.working_directory)

        output_directory = self._apply_formatter(
            formatter=self.output_options.output_directory, entry=entry
        )

        output_file_name = self._apply_formatter(
            formatter=self.output_options.file_name, entry=entry
        )
        entry_destination_file_path = Path(output_directory) / Path(output_file_name)

        os.makedirs(os.path.dirname(entry_destination_file_path), exist_ok=True)
        copyfile(entry_source_file_path, entry_destination_file_path)

        self._archive_entry_file_name(entry=entry, relative_file_name=output_file_name)

        # TODO: move thumbnail to separate function
        # Download the thumbnail if its present
        if self.output_options.thumbnail_name:
            source_thumbnail_path = entry.thumbnail_path(relative_directory=self.working_directory)

            # Bug that mismatches webp and jpg extensions. Try to hotfix here
            if not os.path.isfile(source_thumbnail_path):
                actual_thumbnail_ext = ".webp"
                if entry.thumbnail_ext == "webp":
                    actual_thumbnail_ext = ".jpg"

                source_thumbnail_path = source_thumbnail_path.replace(
                    f".{entry.thumbnail_ext}", actual_thumbnail_ext
                )
                if not os.path.isfile(source_thumbnail_path):
                    # TODO: make more formal
                    raise ValueError("Youtube thumbnails are a lie")

            output_thumbnail_name = self._apply_formatter(
                formatter=self.output_options.thumbnail_name, entry=entry
            )
            output_thumbnail_path = Path(output_directory) / Path(output_thumbnail_name)

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

        if self.metadata_options.nfo:
            self._post_process_nfo(nfo_options=self.metadata_options.nfo, entry=entry)

        if self.metadata_options.output_directory_nfo:
            self._post_process_nfo(nfo_options=self.metadata_options.output_directory_nfo)
