import os
from pathlib import Path
from typing import Optional

from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.xml import to_max_3_byte_utf8_dict
from ytdl_sub.utils.xml import to_max_3_byte_utf8_string
from ytdl_sub.utils.xml import to_xml
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import BoolValidator


class NfoTagsOptions(PluginOptions):
    """
    Adds an NFO file for every download file. An NFO file is simply an XML file
    with a ``.nfo`` extension. You can add any values into the NFO.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           nfo_tags:
             # required
             nfo_name: "{title_sanitized}.nfo"
             nfo_root: "episodedetails"
             tags:
               title: "{title}"
               season: "{upload_year}"
               episode: "{upload_month}{upload_day_padded}"
             # optional
             kodi_safe: False
    """

    _required_keys = {"nfo_name", "nfo_root", "tags"}
    _optional_keys = {"kodi_safe"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self._nfo_name = self._validate_key(key="nfo_name", validator=StringFormatterValidator)
        self._nfo_root = self._validate_key(key="nfo_root", validator=StringFormatterValidator)
        self._tags = self._validate_key(key="tags", validator=DictFormatterValidator)
        self._kodi_safe = self._validate_key_if_present(
            key="kodi_safe", validator=BoolValidator, default=False
        ).value

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

    @property
    def kodi_safe(self) -> Optional[bool]:
        """
        Optional. Kodi does not support > 3-byte unicode characters, which include emojis and some
        foreign language characters. Setting this to True will replace those characters with '□'.
        Defaults to False.
        """
        return self._kodi_safe


class NfoTagsPlugin(Plugin[NfoTagsOptions]):
    plugin_options_type = NfoTagsOptions

    def post_process_entry(self, entry: Entry) -> None:
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

        if self.plugin_options.kodi_safe:
            nfo = to_max_3_byte_utf8_dict(nfo)
            nfo_root = to_max_3_byte_utf8_string(nfo_root)

        xml = to_xml(nfo_dict=nfo, nfo_root=nfo_root)

        nfo_file_name = self.overrides.apply_formatter(
            formatter=self.plugin_options.nfo_name, entry=entry
        )

        # Save the nfo's XML to file
        nfo_file_path = Path(self.working_directory) / nfo_file_name
        os.makedirs(os.path.dirname(nfo_file_path), exist_ok=True)
        with open(nfo_file_path, "wb") as nfo_file:
            nfo_file.write(xml)

        # Save the nfo file and log its metadata
        nfo_metadata = FileMetadata.from_dict(value_dict={nfo_root: nfo}, title="NFO tags:")
        self.save_file(file_name=nfo_file_name, file_metadata=nfo_metadata, entry=entry)
