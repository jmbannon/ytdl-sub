from abc import ABC
from collections import defaultdict
from typing import Dict
from typing import List

from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import ListFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import DictValidator
from ytdl_sub.validators.validators import ListValidator


class NfoTagsWithAttributesValidator(StrictDictValidator):

    _required_keys = {"attributes", "tag"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._attributes = self._validate_key(key="attributes", validator=DictFormatterValidator)
        self._tag = self._validate_key(key="tag", validator=StringFormatterValidator)

    @property
    def attributes(self) -> DictFormatterValidator:
        """
        Returns
        -------
        The attributes for this NFO tag
        """
        return self._attributes

    @property
    def tag(self) -> StringFormatterValidator:
        """
        Returns
        -------
        The value for this NFO tag
        """
        return self._tag


class NfoTagsWithAttributesListValidator(ListValidator[NfoTagsWithAttributesValidator]):
    """TagsWithAttributes list for the entry NFO validator"""

    _inner_list_type = NfoTagsWithAttributesValidator


class NfoTagsValidator(DictValidator, ABC):
    def __init__(self, name, value):
        super().__init__(name, value)

        self._string_tags: Dict[str, List[StringFormatterValidator]] = defaultdict(list)
        self._attribute_tags: Dict[str, List[NfoTagsWithAttributesValidator]] = defaultdict(list)

        for key, tag_value in self._dict.items():
            # Turn each value into a list if it's not
            if not isinstance(tag_value, list):
                tag_value = [tag_value]

            if isinstance(tag_value[0], str):
                self._string_tags[key].extend(
                    self._validate_key(
                        key=key,
                        validator=ListFormatterValidator,
                    ).list
                )
            elif isinstance(tag_value[0], dict):
                self._attribute_tags[key].extend(
                    self._validate_key(key=key, validator=NfoTagsWithAttributesListValidator).list
                )
            else:
                raise self._validation_exception(
                    "must either be a single or list of string/attribute object"
                )

    @property
    def string_tags(self) -> Dict[str, List[StringFormatterValidator]]:
        """
        Returns
        -------
        Tags with no attributes
        """
        return self._string_tags

    @property
    def attribute_tags(self) -> Dict[str, List[NfoTagsWithAttributesValidator]]:
        """
        Returns
        -------
        Tags with attributes
        """
        return self._attribute_tags
