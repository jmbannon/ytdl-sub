from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.nfo_tags import NfoTagsValidator
from ytdl_sub.plugins.nfo_tags import SharedNfoTagsOptions
from ytdl_sub.plugins.nfo_tags import SharedNfoTagsPlugin
from ytdl_sub.utils.xml import XmlElement
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class OutputDirectoryNfoTagsOptions(SharedNfoTagsOptions):
    """
    Adds a single NFO file in the output directory. An NFO file is simply an XML file with a
    ``.nfo`` extension. It builds the tags using each entry's source variables, and merges all the
    unique values into the final set of tags. Be cautious of which variables you use.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           output_directory_nfo_tags:
             # required
             nfo_name: "tvshow.nfo"
             nfo_root: "tvshow"
             tags:
               title: "Sweet youtube TV show"
             # optional
             kodi_safe: False
    """

    @property
    def nfo_root(self) -> StringFormatterValidator:
        """
        The root tag of the NFO's XML. In the usage above, it would look like

        .. code-block:: xml

           <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
           <tvshow>
           </tvshow>
        """
        return self._nfo_root

    @property
    def tags(self) -> NfoTagsValidator:
        """
        Tags within the nfo_root tag. In the usage above, it would look like

        .. code-block:: xml

           <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
           <tvshow>
             <title>Sweet youtube TV show</title>
           </tvshow>

        Also supports xml attributes and duplicate keys:

        .. code-block:: yaml

           tags:
             namedseason:
               - tag: "{season_name}"
                 attributes:
                   number: "{season_index}"
             genre:
               - "Comedy"
               - "Drama"

        With merged tags, it could translate to

        .. code-block:: xml

           <title year="2022">Sweet youtube TV show</season>
           <genre>Comedy</genre>
           <genre>Drama</genre>
           <namedseason number="1">Some Playlist</namedseason>
           <namedseason number="2">Another Playlist</namedseason>
        """
        return self._tags


class OutputDirectoryNfoTagsPlugin(SharedNfoTagsPlugin):
    plugin_options_type = OutputDirectoryNfoTagsOptions

    def __init__(
        self,
        plugin_options: OutputDirectoryNfoTagsOptions,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        super().__init__(plugin_options, overrides, enhanced_download_archive)
        self._nfo_tags: Dict[str, List[XmlElement]] = {}
        self._last_entry: Optional[Entry] = None

    def post_process_entry(self, entry: Entry) -> None:
        """
        Merges the nfo_tags dict of all entries. Tracks the last entry processed
        """
        nfo_tags = self._get_xml_element_dict(entry=entry)
        for key, xml_elements in nfo_tags.items():
            # Key not in nfo_tags, add and continue
            if key not in self._nfo_tags:
                self._nfo_tags[key] = xml_elements
                continue

            # Is in nfo_tags, only add new ones
            for xml_element in xml_elements:
                if xml_element not in self._nfo_tags[key]:
                    self._nfo_tags[key].append(xml_element)

        self._last_entry = entry

    def post_process_subscription(self):
        """
        Creates an NFO file in the root of the output directory using merged nfo tags and last entry
        for the NFO root
        """
        if self._last_entry:
            self._create_nfo(entry=self._last_entry, nfo_tags=self._nfo_tags, save_to_entry=False)
