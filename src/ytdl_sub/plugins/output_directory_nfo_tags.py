import os
from pathlib import Path

import dicttoxml

from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.validators.string_formatter_validators import OverridesDictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator


class OutputDirectoryNfoTagsOptions(PluginOptions):
    """
    Adds a single NFO file in the output directory. An NFO file is simply an XML file  with a
    ``.nfo`` extension. You can add any values into the NFO.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           output_directory_nfo_tags:
             nfo_name: "tvshow.nfo"
             nfo_root: "tvshow"
             tags:
               title: "Sweet youtube TV show"
    """

    _required_keys = {"nfo_name", "nfo_root", "tags"}

    def __init__(self, name, value):
        super().__init__(name, value)
        # Since this does not create NFOs for entries, we must use the overrides formatter classes
        # to ensure we are only using values defined as string literals or in overrides
        self._nfo_name = self._validate_key(
            key="nfo_name", validator=OverridesStringFormatterValidator
        )
        self._nfo_root = self._validate_key(
            key="nfo_root", validator=OverridesStringFormatterValidator
        )
        self._tags = self._validate_key(key="tags", validator=OverridesDictFormatterValidator)

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
    def tags(self) -> OverridesDictFormatterValidator:
        """
        Tags within the nfo_root tag. In the usage above, it would look like

        .. code-block:: xml

           <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
           <tvshow>
             <title>Sweet youtube TV show</title>
           </tvshow>
        """
        return self._tags


class OutputDirectoryNfoTagsPlugin(Plugin[OutputDirectoryNfoTagsOptions]):
    plugin_options_type = OutputDirectoryNfoTagsOptions

    def post_process_subscription(self):
        """
        Creates an NFO file in the root of the output directory
        """
        nfo = {}

        for tag, tag_formatter in sorted(self.plugin_options.tags.dict.items()):
            nfo[tag] = self.overrides.apply_formatter(formatter=tag_formatter)

        # Write the nfo tags to XML with the nfo_root
        nfo_root = self.overrides.apply_formatter(formatter=self.plugin_options.nfo_root)
        xml = dicttoxml.dicttoxml(
            obj=nfo,
            root=True,  # We assume all NFOs have a root. Maybe we should not?
            custom_root=nfo_root,
            attr_type=False,
        )

        nfo_file_name = self.overrides.apply_formatter(formatter=self.plugin_options.nfo_name)

        # Save the nfo's XML to file
        nfo_file_path = Path(self.working_directory) / nfo_file_name
        os.makedirs(os.path.dirname(nfo_file_path), exist_ok=True)
        with open(nfo_file_path, "wb") as nfo_file:
            nfo_file.write(xml)

        self.save_file(file_name=nfo_file_name)
