from abc import ABC
from typing import Dict
from typing import Generic
from typing import Type
from typing import TypeVar

from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesDictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import DictValidator

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
    formatter_validator = StringFormatterValidator
    dict_formatter_validator = DictFormatterValidator


class NfoOverrideTagsWithAttributesValidator(
    _NfoTagsWithAttributesValidator[
        OverridesStringFormatterValidator, OverridesDictFormatterValidator
    ]
):
    formatter_validator = OverridesStringFormatterValidator
    dict_formatter_validator = OverridesDictFormatterValidator


TNfoTagsWithAttributesValidator = _NfoTagsWithAttributesValidator[
    TStringFormatterValidator, TDictFormatterValidator
]


class SharedNfoTagsValidator(
    DictValidator, Generic[TStringFormatterValidator, TDictFormatterValidator], ABC
):

    _tags_with_attributes_validator: Type[TNfoTagsWithAttributesValidator]

    def __init__(self, name, value):
        super().__init__(name, value)

        self._string_tags: Dict[str, StringFormatterValidator] = {}
        self._attribute_tags: Dict[str, TNfoTagsWithAttributesValidator] = {}

        for key, tag_value in self._dict.items():
            if isinstance(tag_value, str):
                self._string_tags[key] = self._validate_key(
                    key=key, validator=self._tags_with_attributes_validator.formatter_validator
                )
            elif isinstance(tag_value, dict):
                self._attribute_tags[key] = self._validate_key(
                    key=key, validator=self._tags_with_attributes_validator
                )
            else:
                raise self._validation_exception("must either be a string or attributes object")

    @property
    def string_tags(self) -> Dict[str, StringFormatterValidator]:
        """
        Returns
        -------
        Tags with no attributes
        """
        return self._string_tags

    @property
    def attribute_tags(self) -> Dict[str, TNfoTagsWithAttributesValidator]:
        """
        Returns
        -------
        Tags with attributes
        """
        return self._attribute_tags


class NfoTagsValidator(SharedNfoTagsValidator[StringFormatterValidator, DictFormatterValidator]):
    _tags_with_attributes_validator = NfoTagsWithAttributesValidator


class NfoOverrideTagsValidator(
    SharedNfoTagsValidator[OverridesStringFormatterValidator, OverridesDictFormatterValidator]
):
    _tags_with_attributes_validator = NfoOverrideTagsWithAttributesValidator
