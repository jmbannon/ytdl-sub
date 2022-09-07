import xml.etree.ElementTree as et
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Union


@dataclass
class XmlElement:
    text: str
    attributes: Dict[str, str]

    def to_dict_value(self) -> Union[str, Dict[str, Any]]:
        """
        Returns
        -------
        Only the tag if no attributes, otherwise a dict containing both attributes and the tag
        """
        if not self.attributes:
            return self.text
        return {
            "attributes": self.attributes,
            "tag": self.text,
        }


def _to_max_3_byte_utf8_char(char: str) -> str:
    return "□" if len(char.encode("utf-8")) > 3 else char


def to_max_3_byte_utf8_string(string: str) -> str:
    """
    Parameters
    ----------
    string
        input string

    Returns
    -------
    Casted unicode string
    """
    return "".join(_to_max_3_byte_utf8_char(char) for char in string)


def to_max_3_byte_utf8_dict(string_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Parameters
    ----------
    string_dict
        Input string dict

    Returns
    -------
    Casted dict
    """
    return {
        to_max_3_byte_utf8_string(key): to_max_3_byte_utf8_string(value)
        for key, value in string_dict.items()
    }


def to_xml(nfo_dict: Dict[str, List[XmlElement]], nfo_root: str) -> bytes:
    """
    Transforms a dict to XML

    Parameters
    ----------
    nfo_dict
        XML contents
    nfo_root
        Root of the XML

    Returns
    -------
    XML bytes
    """
    xml_root = et.Element(nfo_root)
    for key, xml_elems in sorted(nfo_dict.items()):
        for xml_elem in xml_elems:
            sorted_attr = dict(sorted(xml_elem.attributes.items()))
            sub_element = et.SubElement(xml_root, key, sorted_attr)
            sub_element.text = xml_elem.text

    et.indent(tree=xml_root, space="  ", level=0)
    return et.tostring(element=xml_root, encoding="utf-8", xml_declaration=True)
