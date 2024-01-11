import os
from abc import ABC
from collections import defaultdict
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.validators.options import ToggleableOptionsDictValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.xml import XmlElement
from ytdl_sub.utils.xml import to_max_3_byte_utf8_dict
from ytdl_sub.utils.xml import to_max_3_byte_utf8_string
from ytdl_sub.utils.xml import to_xml
from ytdl_sub.validators.file_path_validators import StringFormatterFileNameValidator
from ytdl_sub.validators.nfo_validators import NfoTagsValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import BoolValidator


class SharedNfoTagsOptions(ToggleableOptionsDictValidator):
    """
    Shared code between NFO tags and Ouptut Directory NFO Tags
    """

    _required_keys = {"nfo_name", "nfo_root", "tags"}
    _optional_keys = {"enable", "kodi_safe"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate NFO tag options
        """
        if isinstance(value, dict):
            value["nfo_name"] = value.get("nfo_name", "placeholder")
            value["nfo_root"] = value.get("nfo_root", "placeholder")
            value["tags"] = value.get("tags", {})

        _ = cls(name=name, value=value)

    def __init__(self, name, value):
        super().__init__(name, value)

        self._nfo_name = self._validate_key_if_present(
            key="nfo_name", validator=StringFormatterFileNameValidator
        )
        self._nfo_root = self._validate_key_if_present(
            key="nfo_root", validator=StringFormatterValidator
        )
        self._tags = self._validate_key_if_present(key="tags", validator=NfoTagsValidator)
        self._kodi_safe = self._validate_key_if_present(
            key="kodi_safe", validator=BoolValidator, default=False
        ).value

    @property
    def nfo_name(self) -> StringFormatterFileNameValidator:
        """
        :expected type: EntryFormatter
        :description:
          The NFO file name.
        """
        return self._nfo_name

    @property
    def nfo_root(self) -> StringFormatterValidator:
        """
        OVERRIDE DOC IN CHILD CLASSES
        """
        return self._nfo_root

    @property
    def tags(self) -> NfoTagsValidator:
        """
        OVERRIDE DOC IN CHILD CLASSES
        """
        return self._tags

    @property
    def kodi_safe(self) -> Optional[bool]:
        """
        :expected type: Optional[Boolean]
        :description:
          Defaults to False. Kodi does not support > 3-byte unicode characters, which include
          emojis and some foreign language characters. Setting this to True will replace those
          characters with '□'.
        """
        return self._kodi_safe


class SharedNfoTagsPlugin(Plugin[SharedNfoTagsOptions], ABC):
    """
    Shared code between NFO tags and Ouptut Directory NFO Tags
    """

    def _get_xml_element_dict(self, entry: Entry) -> Dict[str, List[XmlElement]]:
        nfo_tags: Dict[str, List[XmlElement]] = defaultdict(list)

        for key, string_tags in self.plugin_options.tags.string_tags.items():
            tags = [
                XmlElement(
                    text=self.overrides.apply_formatter(formatter=string_tag, entry=entry),
                    attributes={},
                )
                for string_tag in string_tags
            ]
            # Do not add tags with empty text
            nfo_tags[key].extend(tag for tag in tags if tag.text)

        for key, attribute_tags in self.plugin_options.tags.attribute_tags.items():
            tags = [
                XmlElement(
                    text=self.overrides.apply_formatter(formatter=attribute_tag.tag, entry=entry),
                    attributes={
                        attr_name: self.overrides.apply_formatter(
                            formatter=attr_formatter, entry=entry
                        )
                        for attr_name, attr_formatter in attribute_tag.attributes.dict.items()
                    },
                )
                for attribute_tag in attribute_tags
            ]
            # Do not add tags with empty text
            nfo_tags[key].extend(tag for tag in tags if tag.text)

        # Do not add tags with empty lists
        return {key: tags for key, tags in nfo_tags.items() if len(tags) > 0}

    def _create_nfo(self, entry: Entry, save_to_entry: bool = True) -> None:
        # Write the nfo tags to XML with the nfo_root
        nfo_root = self.overrides.apply_formatter(
            formatter=self.plugin_options.nfo_root, entry=entry
        )
        nfo_tags = self._get_xml_element_dict(entry=entry)

        # If the nfo tags are empty, then stop continuing
        if not nfo_tags:
            return

        if self.plugin_options.kodi_safe:
            nfo_root = to_max_3_byte_utf8_string(nfo_root)
            nfo_tags = {
                to_max_3_byte_utf8_string(key): [
                    XmlElement(
                        text=to_max_3_byte_utf8_string(xml_elem.text),
                        attributes=to_max_3_byte_utf8_dict(xml_elem.attributes),
                    )
                    for xml_elem in xml_elems
                ]
                for key, xml_elems in nfo_tags.items()
            }

        xml = to_xml(nfo_dict=nfo_tags, nfo_root=nfo_root)

        nfo_file_name = self.overrides.apply_formatter(
            formatter=self.plugin_options.nfo_name, entry=entry
        )

        # Save the nfo's XML to file
        nfo_file_path = Path(self.working_directory) / nfo_file_name
        os.makedirs(os.path.dirname(nfo_file_path), exist_ok=True)
        with open(nfo_file_path, "wb") as nfo_file:
            nfo_file.write(xml)

        # Save the nfo file and log its metadata
        nfo_metadata = FileMetadata.from_dict(
            value_dict={
                nfo_root: {
                    key: (
                        xml_elems[0].to_dict_value()
                        if len(xml_elems) == 1
                        else [xml_elem.to_dict_value() for xml_elem in xml_elems]
                    )
                    for key, xml_elems in nfo_tags.items()
                }
            },
            title="NFO tags",
        )

        if save_to_entry:
            self.save_file(file_name=nfo_file_name, file_metadata=nfo_metadata, entry=entry)
        else:
            self.save_file(file_name=nfo_file_name, file_metadata=nfo_metadata)

        FileHandler.delete(nfo_file_path)


class NfoTagsOptions(SharedNfoTagsOptions):
    """
    Adds an NFO file for every download file. An NFO file is simply an XML file
    with a ``.nfo`` extension. You can add any values into the NFO.

    :Usage:

    .. code-block:: yaml

       nfo_tags:
         nfo_name: "{title_sanitized}.nfo"
         nfo_root: "episodedetails"
         tags:
           title: "{title}"
           season: "{upload_year}"
           episode: "{upload_month}{upload_day_padded}"
         kodi_safe: False
    """

    _formatter_validator = StringFormatterValidator
    _dict_formatter_validator = DictFormatterValidator
    _tags_validator = NfoTagsValidator

    @property
    def nfo_root(self) -> StringFormatterValidator:
        """
        :expected type: EntryFormatter
        :description:
          The root tag of the NFO's XML. In the usage above, it would look like

          .. code-block:: xml

             <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
             <episodedetails>
             </episodedetails>
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
             <episodedetails>
               <title>Awesome Youtube Video</title>
               <season>2022</season>
               <episode>502</episode>
             </episodedetails>

          Also supports xml attributes and duplicate keys:

          .. code-block:: yaml

             tags:
               season:
                 attributes:
                   name: "Best Year"
                 tag: "{upload_year}"
               genre:
                 - "Comedy"
                 - "Drama"

          Which translates to

          .. code-block:: xml

             <season name="Best Year">2022</season>
             <genre>Comedy</genre>
             <genre>Drama</genre>
        """
        return self._tags


class NfoTagsPlugin(SharedNfoTagsPlugin):
    plugin_options_type = NfoTagsOptions

    def post_process_entry(self, entry: Entry) -> None:
        """
        Creates an entry's NFO file using values defined in the metadata options

        Parameters
        ----------
        entry:
            Entry to create an NFO file for
        """
        self._create_nfo(entry=entry)
