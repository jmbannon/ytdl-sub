from typing import Dict

import xml.etree.ElementTree as et


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


def to_xml(nfo_dict: Dict[str, str], nfo_root: str) -> str:
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
    for key, value in nfo_dict.items():
        et.SubElement(xml_root, value)

    return et.tostring(element=xml_root, encoding='utf-8', xml_declaration=True)

