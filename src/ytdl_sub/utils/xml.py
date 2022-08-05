from typing import Dict

import dicttoxml


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


def to_xml(nfo_dict: Dict[str, str], nfo_root: str) -> bytes:
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
    return dicttoxml.dicttoxml(
        obj=nfo_dict,
        root=True,
        custom_root=nfo_root,
        attr_type=False,
    )
