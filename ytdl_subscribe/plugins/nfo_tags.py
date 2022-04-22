import os
from pathlib import Path

import dicttoxml

from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.plugins.plugin import Plugin
from ytdl_subscribe.plugins.plugin import PluginOptions
from ytdl_subscribe.validators.string_formatter_validators import DictFormatterValidator
from ytdl_subscribe.validators.string_formatter_validators import StringFormatterValidator


class NfoTagsOptions(PluginOptions):
    _required_keys = {"nfo_name", "nfo_root", "tags"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self.nfo_name = self._validate_key(key="nfo_name", validator=StringFormatterValidator)
        self.nfo_root = self._validate_key(key="nfo_root", validator=StringFormatterValidator)
        self.tags = self._validate_key(key="tags", validator=DictFormatterValidator)


class NfoTagsPlugin(Plugin[NfoTagsOptions]):
    plugin_options_type = NfoTagsOptions

    def post_process_entry(self, entry: Entry):
        """
        Creates an entry's NFO file using values defined in the metadata options

        Parameters
        ----------
        entry: Entry to create an NFO file for
        """
        nfo = {}

        for tag, tag_formatter in self.plugin_options.tags.dict.items():
            nfo[tag] = self.overrides.apply_formatter(formatter=tag_formatter, entry=entry)

        # Write the nfo tags to XML with the nfo_root
        nfo_root = self.overrides.apply_formatter(
            formatter=self.plugin_options.nfo_root, entry=entry
        )
        xml = dicttoxml.dicttoxml(
            obj=nfo,
            root=True,  # We assume all NFOs have a root. Maybe we should not?
            custom_root=nfo_root,
            attr_type=False,
        )

        nfo_file_name = self.overrides.apply_formatter(
            formatter=self.plugin_options.nfo_name, entry=entry
        )

        # Save the nfo's XML to file
        nfo_file_path = Path(self.output_directory) / nfo_file_name
        os.makedirs(os.path.dirname(nfo_file_path), exist_ok=True)
        with open(nfo_file_path, "wb") as nfo_file:
            nfo_file.write(xml)

        # Archive the nfo's file name
        self.archive_entry_file_name(entry=entry, relative_file_path=nfo_file_name)
