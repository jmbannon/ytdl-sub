from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.nfo_tags import NfoTagsValidator
from ytdl_sub.plugins.nfo_tags import SharedNfoTagsOptions
from ytdl_sub.plugins.nfo_tags import SharedNfoTagsPlugin
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator


class StaticNfoTagsOptions(SharedNfoTagsOptions):
    """
    Adds an NFO file for every entry, but does not link it to an entry in the download
    archive.  This is intended to produce ``season.nfo`` files in each season
    directory. Each entry within a season will overwrite this file with its season
    name. If the entry gets deleted from ytdl-sub, this file will remain since it's not
    linked.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           static_nfo_tags:
             # required
             nfo_name: "season.nfo"
             nfo_root: "season"
             tags:
               title: "My custom season name!"
             # optional
             kodi_safe: False
    """

    @property
    def nfo_root(self) -> StringFormatterValidator:
        """
        :expected type: EntryFormatter
        :description:
          The root tag of the NFO's XML. In the usage above, it would look like

          .. code-block:: xml

             <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
             <season>
             </season>
        """
        return self._nfo_root

    @property
    def tags(self) -> NfoTagsValidator:
        """
        :expected type: NfoTags
        :description:
          Tags within the nfo_root tag. In the usage above, it would look like

          .. code-block:: xml

             <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
             <season>
               <title>My custom season name!</title>
             </season>
        """
        return self._tags


class StaticNfoTagsPlugin(SharedNfoTagsPlugin):
    plugin_options_type = StaticNfoTagsOptions

    def post_process_entry(self, entry: Entry) -> None:
        """
        Creates the NFO from each entry, but does not link/save it to the entry.
        """
        self._create_nfo(entry=entry, save_to_entry=False)
