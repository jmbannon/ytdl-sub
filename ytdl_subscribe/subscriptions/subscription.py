import os
from pathlib import Path
from shutil import copyfile
from typing import Type
from typing import TypeVar

import dicttoxml
import music_tag
from PIL import Image

from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.validators.config.config_validator import ConfigValidator
from ytdl_subscribe.validators.config.metadata_options.metadata_options_validator import (
    MetadataOptionsValidator,
)
from ytdl_subscribe.validators.config.output_options.output_options_validator import (
    OutputOptionsValidator,
)
from ytdl_subscribe.validators.config.preset_validator import OverridesValidator
from ytdl_subscribe.validators.config.preset_validator import YTDLOptionsValidator
from ytdl_subscribe.validators.config.sources.source_validator import (
    DownloadStrategyValidator,
)
from ytdl_subscribe.validators.config.sources.source_validator import SourceValidator

SOURCE_T = TypeVar("SOURCE_T", bound=SourceValidator)
DOWNLOAD_STRATEGY_T = TypeVar("DOWNLOAD_STRATEGY_T", bound=DownloadStrategyValidator)


class Subscription(object):
    source_validator_type: Type[SOURCE_T]
    download_strategy_type: Type[DOWNLOAD_STRATEGY_T]

    def __init__(
        self,
        name: str,
        config_options: ConfigValidator,
        source_options: SourceValidator,
        output_options: OutputOptionsValidator,
        metadata_options: MetadataOptionsValidator,
        ytdl_options: YTDLOptionsValidator,
        overrides: OverridesValidator,
    ):
        """
        Parameters
        ----------
        name: str
            Name of the subscription
        config_options: ConfigValidator
        source_options: SourceValidator
        output_options: OutputOptionsValidator
        metadata_options: MetadataOptionsValidator
        ytdl_options: YTDLOptionsValidator
        overrides: OverridesValidator
        """
        self.name = name
        self.config_options = config_options

        self.__source_options = source_options
        self.__download_strategy_options = source_options.download_strategy

        if not isinstance(self.__source_options, self.source_validator_type):
            raise ValueError("Source options does not match the expected type")

        if not isinstance(
            self.__download_strategy_options, self.download_strategy_type
        ):
            raise ValueError("Download strategy does not match the expected type")

        self.output_options = output_options
        self.metadata_options = metadata_options
        self.ytdl_options = ytdl_options
        self.overrides = overrides

    @property
    def source_options(self) -> SOURCE_T:
        return self.__source_options

    @property
    def download_strategy_options(self) -> DOWNLOAD_STRATEGY_T:
        return self.__download_strategy_options

    def _post_process_tagging(self, entry: Entry):
        id3_options = self.metadata_options.id3
        t = music_tag.load_file(
            entry.file_path(
                relative_directory=self.config_options.working_directory.value
            )
        )
        for tag, tag_formatter in id3_options.tags.dict.items():
            t[tag] = entry.apply_formatter(
                format_string=tag_formatter, overrides=self.overrides.dict
            )
        t.save()

    def _post_process_nfo(self, entry):
        nfo = {}
        nfo_options = self.metadata_options.nfo

        for tag, tag_formatter in nfo_options.tags.dict.items():
            nfo[tag] = entry.apply_formatter(
                format_string=tag_formatter, overrides=self.overrides
            )

        xml = dicttoxml.dicttoxml(
            obj=nfo,
            root=True,  # We assume all NFOs have a root. Maybe we should not?
            custom_root=nfo_options.nfo_root.value,
            attr_type=False,
        )
        nfo_file_path = entry.apply_formatter(
            format_string=nfo_options.nfo_name.format_string,
            overrides=self.overrides.dict,
        )
        with open(nfo_file_path, "wb") as f:
            f.write(xml)

    def extract_info(self):
        """
        Extracts only the info of the source, does not download it
        """
        raise NotImplemented("Each source needs to implement how it extracts info")

    def post_process_entry(self, entry: Entry):
        if self.metadata_options.id3:
            self._post_process_tagging(entry)

        # Move the file after all direct file modifications are complete
        entry_source_file_path = entry.file_path(
            relative_directory=self.config_options.working_directory.value
        )

        output_directory = entry.apply_formatter(
            format_string=self.output_options.output_directory.format_string,
            overrides=self.overrides.dict,
        )
        output_file_name = entry.apply_formatter(
            format_string=self.output_options.file_name.format_string,
            overrides=self.overrides.dict,
        )
        entry_destination_file_path = Path(output_directory) / Path(output_file_name)

        os.makedirs(os.path.dirname(entry_destination_file_path), exist_ok=True)
        copyfile(entry_source_file_path, entry_destination_file_path)

        # Download the thumbnail if its present
        if self.output_options.thumbnail_name:
            source_thumbnail_path = entry.thumbnail_path(
                relative_directory=self.config_options.working_directory.value
            )

            output_thumbnail_name = entry.apply_formatter(
                format_string=self.output_options.thumbnail_name.format_string,
                overrides=self.overrides.dict,
            )
            output_thumbnail_path = Path(output_directory) / Path(output_thumbnail_name)

            os.makedirs(os.path.dirname(output_thumbnail_path), exist_ok=True)

            # If the thumbnail is to be converted, then save the converted thumbnail to the
            # output filepath
            if self.output_options.convert_thumbnail:
                im = Image.open(source_thumbnail_path).convert("RGB")
                im.save(
                    fp=output_thumbnail_name,
                    format=self.output_options.convert_thumbnail.value,
                )
            # Otherwise, just copy the downloaded thumbnail
            else:
                copyfile(source_thumbnail_path, output_thumbnail_name)

        if self.metadata_options.nfo:
            self._post_process_nfo(entry)
