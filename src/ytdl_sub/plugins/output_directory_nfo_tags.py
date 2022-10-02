from typing import Optional

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.nfo_tags import NfoTagsValidator
from ytdl_sub.plugins.nfo_tags import SharedNfoTagsOptions
from ytdl_sub.plugins.nfo_tags import SharedNfoTagsPlugin
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class OutputDirectoryNfoTagsOptions(SharedNfoTagsOptions):
    """
    Adds a single NFO file in the output directory. An NFO file is simply an XML file with a
    ``.nfo`` extension. It uses the last entry's source variables which can change per download
    invocation. Be cautious of which variables you use.

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

    # Hack to make it so collection named seasons do not error
    # when adding output_directory_nfo info for plex
    _required_keys = set()
    _optional_keys = {"kodi_safe", "nfo_name", "nfo_root", "tags"}

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
             named_season:
               - tag: "{source_title}"
                 attributes:
                   number: "{collection_index}"
                 behavior: "merge"
             genre:
               - tag: "Comedy"
                 behavior: "overwrite"
               - "Comedy"
               - "Drama"

        Which translates to

        .. code-block:: xml

           <title year="2022">Sweet youtube TV show</season>
           <genre>Comedy</genre>
           <genre>Drama</genre>
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
        self._last_entry: Optional[Entry] = None

    def post_process_entry(self, entry: Entry) -> None:
        """
        Tracks the last entry processed
        """
        self._last_entry = entry

    def post_process_subscription(self):
        """
        Creates an NFO file in the root of the output directory using the last entry
        """
        if (
            self.plugin_options.nfo_name is None
            or self.plugin_options.nfo_root is None
            or self._last_entry is None
        ):
            return

        self._create_nfo(entry=self._last_entry, save_to_entry=False)
