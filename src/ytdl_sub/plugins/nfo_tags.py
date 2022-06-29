import os
from pathlib import Path

import dicttoxml

from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator


class NfoTagsOptions(PluginOptions):
    """
    Adds an NFO file for every download file. An NFO file is simply an XML file
    with a ``.nfo`` extension. You can add any values into the NFO.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           nfo:
            nfo_name: "{title_sanitized}.nfo"
            nfo_root: "episodedetails"
            tags:
              title: "{title}"
              season: "{upload_year}"
              episode: "{upload_month}{upload_day_padded}"
    """

    _required_keys = {"nfo_name", "nfo_root", "tags"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self._nfo_name = self._validate_key(key="nfo_name", validator=StringFormatterValidator)
        self._nfo_root = self._validate_key(key="nfo_root", validator=StringFormatterValidator)
        self._tags = self._validate_key(key="tags", validator=DictFormatterValidator)

    @property
    def nfo_name(self) -> StringFormatterValidator:
        """
        The NFO file name.
        """
        return self._nfo_name

    @property
    def nfo_root(self) -> StringFormatterValidator:
        """
        The root tag of the NFO's XML. In the usage above, it would look like

        .. code-block:: xml

           <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
           <episodedetails>
           </episodedetails>
        """
        return self._nfo_root

    @property
    def tags(self) -> DictFormatterValidator:
        """
        Tags within the nfo_root tag. In the usage above, it would look like

        .. code-block:: xml

           <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
           <episodedetails>
             <title>Awesome Youtube Video</title>
             <season>2022</season>
             <episode>502</episode>
           </episodedetails>
        """
        return self._tags


class NfoTagsPlugin(Plugin[NfoTagsOptions]):
    plugin_options_type = NfoTagsOptions

    def post_process_entry(self, entry: Entry):
        """
        Creates an entry's NFO file using values defined in the metadata options

        Parameters
        ----------
        entry:
            Entry to create an NFO file for
        """
        nfo = {}

        for tag, tag_formatter in sorted(self.plugin_options.tags.dict.items()):
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
        nfo_file_path = Path(self.working_directory) / nfo_file_name
        os.makedirs(os.path.dirname(nfo_file_path), exist_ok=True)
        with open(nfo_file_path, "wb") as nfo_file:
            nfo_file.write(xml)

        # Archive the nfo's file name
        self.save_file(file_name=nfo_file_name, entry=entry)
