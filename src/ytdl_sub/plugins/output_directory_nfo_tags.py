from typing import Optional

from ytdl_sub.plugins.nfo_tags import NfoTagsValidator
from ytdl_sub.plugins.nfo_tags import SharedNfoTagsOptions
from ytdl_sub.plugins.nfo_tags import SharedNfoTagsPlugin
from ytdl_sub.validators.nfo_validators import NfoOverrideTagsValidator
from ytdl_sub.validators.string_formatter_validators import OverridesDictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator


class OutputDirectoryNfoTagsOptions(
    SharedNfoTagsOptions[OverridesStringFormatterValidator, OverridesDictFormatterValidator]
):
    """
    Adds a single NFO file in the output directory. An NFO file is simply an XML file  with a
    ``.nfo`` extension. You can add any values into the NFO.

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

    _formatter_validator = OverridesStringFormatterValidator
    _dict_formatter_validator = OverridesDictFormatterValidator
    _tags_validator = NfoOverrideTagsValidator

    @property
    def nfo_name(self) -> OverridesStringFormatterValidator:
        """
        The NFO file name.
        """
        return self._nfo_name

    @property
    def nfo_root(self) -> OverridesStringFormatterValidator:
        """
        The root tag of the NFO's XML. In the usage above, it would look like

        .. code-block:: xml

           <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
           <tvshow>
           </tvshow>
        """
        return self._nfo_root

    @property
    def tags(
        self,
    ) -> NfoTagsValidator:
        """
        Tags within the nfo_root tag. In the usage above, it would look like

        .. code-block:: xml

           <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
           <tvshow>
             <title>Sweet youtube TV show</title>
           </tvshow>
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


class OutputDirectoryNfoTagsPlugin(
    SharedNfoTagsPlugin[OverridesStringFormatterValidator, OverridesDictFormatterValidator]
):
    plugin_options_type = OutputDirectoryNfoTagsOptions

    def post_process_subscription(self):
        """
        Creates an NFO file in the root of the output directory
        """
        self._create_nfo()
