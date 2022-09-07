from abc import ABC
from collections import defaultdict
from typing import Dict
from typing import Generic
from typing import List
from typing import Type
from typing import TypeVar

from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator, \
    ListFormatterValidator, ListOverridesFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesDictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import DictValidator
from ytdl_sub.validators.validators import ListValidator

TStringFormatterValidator = TypeVar("TStringFormatterValidator", bound=StringFormatterValidator)
TDictFormatterValidator = TypeVar("TDictFormatterValidator", bound=DictFormatterValidator)


class _NfoTagsWithAttributesValidator(
    StrictDictValidator, Generic[TStringFormatterValidator, TDictFormatterValidator], ABC
):

    _required_keys = {"attributes", "tag"}

    formatter_validator: Type[TStringFormatterValidator]
    dict_formatter_validator: Type[TDictFormatterValidator]

    def __init__(self, name, value):
        super().__init__(name, value)
        self._attributes = self._validate_key(
            key="attributes", validator=self.dict_formatter_validator
        )
        self._tag = self._validate_key(key="tag", validator=self.formatter_validator)

    @property
    def attributes(self) -> TDictFormatterValidator:
        """
        Returns
        -------
        The attributes for this NFO tag
        """
        return self._attributes

    @property
    def tag(self) -> TStringFormatterValidator:
        """
        Returns
        -------
        The value for this NFO tag
        """
        return self._tag


class NfoTagsWithAttributesValidator(
    _NfoTagsWithAttributesValidator[StringFormatterValidator, DictFormatterValidator]
):
    """TagsWithAttributes for the entry NFO validator"""

    formatter_validator = StringFormatterValidator
    dict_formatter_validator = DictFormatterValidator


class NfoTagsWithAttributesListValidator(ListValidator[NfoTagsWithAttributesValidator]):
    """TagsWithAttributes list for the entry NFO validator"""

    _inner_list_type = NfoTagsWithAttributesValidator


class NfoOverrideTagsWithAttributesValidator(
    _NfoTagsWithAttributesValidator[
        OverridesStringFormatterValidator, OverridesDictFormatterValidator
    ]
):
    """TagsWithAttributes for the output directory NFO validator"""

    formatter_validator = OverridesStringFormatterValidator
    dict_formatter_validator = OverridesDictFormatterValidator


class NfoOverrideTagsWithAttributesListValidator(
    ListValidator[NfoOverrideTagsWithAttributesValidator]
):
    """TagsWithAttributes list for the output directory NFO validator"""
    _inner_list_type = NfoOverrideTagsWithAttributesValidator


# Generic TagsWithAttribute to use for SharedNfoTagsValidator
TNfoTagsWithAttributesValidator = _NfoTagsWithAttributesValidator[TStringFormatterValidator, TDictFormatterValidator]

# List validators
TNfoTagsWithAttributesListValidator = ListValidator[TNfoTagsWithAttributesValidator]
TNfoTagsListValidator = ListValidator[TStringFormatterValidator]


class SharedNfoTagsValidator(
    DictValidator, ABC
):
    _tags_validator: Type[TNfoTagsListValidator]
    _tags_with_attributes_validator: Type[TNfoTagsWithAttributesListValidator]

    def __init__(self, name, value):
        super().__init__(name, value)

        self._string_tags: Dict[str, List[TStringFormatterValidator]] = defaultdict(list)
        self._attribute_tags: Dict[str, List[TNfoTagsWithAttributesValidator]] = defaultdict(list)

        for key, tag_value in self._dict.items():
            # Turn each value into a list if it's not
            if not isinstance(tag_value, list):
                tag_value = [tag_value]

            if isinstance(tag_value[0], str):
                self._string_tags[key].extend(
                    self._validate_key(
                        key=key,
                        validator=self._tags_validator,
                    ).list
                )
            elif isinstance(tag_value[0], dict):
                self._attribute_tags[key].extend(
                    self._validate_key(
                        key=key, validator=self._tags_with_attributes_validator
                    ).list
                )
            else:
                raise self._validation_exception(
                    "must either be a single or list of string/attribute object"
                )

    @property
    def string_tags(self) -> Dict[str, List[TStringFormatterValidator]]:
        """
        Returns
        -------
        Tags with no attributes
        """
        return self._string_tags

    @property
    def attribute_tags(self) -> Dict[str, List[TNfoTagsWithAttributesValidator]]:
        """
        Returns
        -------
        Tags with attributes
        """
        return self._attribute_tags


class NfoTagsValidator(SharedNfoTagsValidator):
    _tags_validator = ListFormatterValidator
    _tags_with_attributes_validator = NfoTagsWithAttributesListValidator


class NfoOverrideTagsValidator(SharedNfoTagsValidator):
    _tags_validator = ListOverridesFormatterValidator
    _tags_with_attributes_validator = NfoOverrideTagsWithAttributesListValidator
