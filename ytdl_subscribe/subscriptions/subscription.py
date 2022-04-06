import os
from pathlib import Path
from shutil import copyfile
from typing import Type
from typing import TypeVar

import dicttoxml
import music_tag
from PIL import Image

from ytdl_subscribe.downloaders.downloader import Downloader
from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.validators.base.string_formatter_validators import (
    StringFormatterValidator,
)
from ytdl_subscribe.validators.config.config_options.config_options_validator import (
    ConfigOptionsValidator,
)
from ytdl_subscribe.validators.config.preset_validator import PresetValidator
from ytdl_subscribe.validators.config.source_options.source_validator import (
    DownloadStrategyValidator,
)
from ytdl_subscribe.validators.config.source_options.source_validator import (
    SourceValidator,
)

SOURCE_T = TypeVar("SOURCE_T", bound=SourceValidator)
DOWNLOAD_STRATEGY_T = TypeVar("DOWNLOAD_STRATEGY_T", bound=DownloadStrategyValidator)
DOWNLOADER_T = TypeVar("DOWNLOADER_T", bound=Downloader)


class Subscription(object):
    source_validator_type: Type[SOURCE_T]
    download_strategy_type: Type[DOWNLOAD_STRATEGY_T]
    downloader_type: Type[Downloader]

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
        self.output_options = preset_options.output_options
        self.metadata_options = preset_options.metadata_options
        self.ytdl_options = preset_options.ytdl_options
        self.overrides = preset_options.overrides
        self._config_options = config_options
        self._source_options = preset_options.subscription_source
        self._download_strategy_options = self._source_options.download_strategy

        if not isinstance(self._source_options, self.source_validator_type):
            raise ValueError("Source options does not match the expected type")

        if not isinstance(self._download_strategy_options, self.download_strategy_type):
            raise ValueError("Download strategy does not match the expected type")

    @property
    def source_options(self) -> SOURCE_T:
        return self._source_options

    @property
    def download_strategy_options(self) -> DOWNLOAD_STRATEGY_T:
        return self._download_strategy_options

    @property
    def working_directory(self) -> str:
        """Returns the directory that the downloader saves files to"""
        return str(Path(self._config_options.working_directory.value) / Path(self.name))

    @property
    def downloader(self) -> DOWNLOADER_T:
        return self.downloader_type(
            output_directory=self.working_directory,
            ytdl_options=self.ytdl_options.dict,
        )

    def _apply_formatter(
        self, entry: Entry, formatter: StringFormatterValidator
    ) -> str:
        """
        Parameters
        ----------
        entry
            Entry with values to use in the formatter
        formatter
            The formatter itself

        Returns
        -------
        The format_string after .format has been called on it using entry and override values
        """
        variable_dict = dict(entry.to_dict(), **self.overrides.dict_with_format_strings)
        return formatter.apply_formatter(variable_dict)

    def _post_process_tagging(self, entry: Entry):
        id3_options = self.metadata_options.id3
        audio_file = music_tag.load_file(
            entry.file_path(relative_directory=self.working_directory)
        )
        for tag, tag_formatter in id3_options.tags.dict.items():
            audio_file[tag] = self._apply_formatter(
                entry=entry, formatter=tag_formatter
            )
        audio_file.save()

    def _post_process_nfo(self, entry):
        nfo = {}
        nfo_options = self.metadata_options.nfo

        for tag, tag_formatter in nfo_options.tags.dict.items():
            nfo[tag] = self._apply_formatter(entry=entry, formatter=tag_formatter)

        # Write the nfo tags to XML with the nfo_root
        nfo_root = self._apply_formatter(entry=entry, formatter=nfo_options.nfo_root)
        xml = dicttoxml.dicttoxml(
            obj=nfo,
            root=True,  # We assume all NFOs have a root. Maybe we should not?
            custom_root=nfo_root,
            attr_type=False,
        )

        nfo_file_name = self._apply_formatter(
            entry=entry, formatter=nfo_options.nfo_name
        )
        output_directory = self._apply_formatter(
            entry=entry, formatter=self.output_options.output_directory
        )

        # Save the nfo's XML to file
        nfo_file_path = Path(output_directory) / Path(nfo_file_name)
        with open(nfo_file_path, "wb") as nfo_file:
            nfo_file.write(xml)

    def extract_info(self):
        """
        Extracts only the info of the source, does not download it
        """
        raise NotImplementedError("Each source needs to implement how it extracts info")

    def post_process_entry(self, entry: Entry):
        if self.metadata_options.id3:
            self._post_process_tagging(entry)

        # Move the file after all direct file modifications are complete
        entry_source_file_path = entry.file_path(
            relative_directory=self.working_directory
        )

        output_directory = self._apply_formatter(
            entry=entry, formatter=self.output_options.output_directory
        )

        output_file_name = self._apply_formatter(
            entry=entry, formatter=self.output_options.file_name
        )
        entry_destination_file_path = Path(output_directory) / Path(output_file_name)

        os.makedirs(os.path.dirname(entry_destination_file_path), exist_ok=True)
        copyfile(entry_source_file_path, entry_destination_file_path)

        # Download the thumbnail if its present
        if self.output_options.thumbnail_name:
            source_thumbnail_path = entry.thumbnail_path(
                relative_directory=self.working_directory
            )

            output_thumbnail_name = self._apply_formatter(
                entry=entry, formatter=self.output_options.thumbnail_name
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

        if self.metadata_options.nfo:
            self._post_process_nfo(entry)
