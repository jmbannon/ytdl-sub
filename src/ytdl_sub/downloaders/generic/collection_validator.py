from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.config.preset_options import AddsVariablesMixin
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import ListValidator


class CollectionThumbnailValidator(StrictDictValidator):
    _required_keys = {"name", "uid"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self._name = self._validate_key(key="name", validator=StringFormatterValidator)
        self._uid = self._validate_key(key="uid", validator=OverridesStringFormatterValidator)

    @property
    def name(self) -> StringFormatterValidator:
        """
        File name for the thumbnail
        """
        return self._name

    @property
    def uid(self) -> OverridesStringFormatterValidator:
        """
        yt-dlp's unique ID of the thumbnail
        """
        return self._uid


class CollectionThumbnailListValidator(ListValidator[CollectionThumbnailValidator]):
    _inner_list_type = CollectionThumbnailValidator


class CollectionUrlValidator(StrictDictValidator):
    _required_keys = {"url"}
    _optional_keys = {"variables", "source_thumbnails", "playlist_thumbnails"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate a YouTube collection url
        """
        if isinstance(value, dict):
            value["url"] = value.get("url", "placeholder")
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)

        # TODO: url validate using yt-dlp IE
        self._url = self._validate_key(key="url", validator=OverridesStringFormatterValidator)
        self._variables = self._validate_key_if_present(
            key="variables", validator=DictFormatterValidator, default={}
        )

        self._source_thumbnails = self._validate_key_if_present(
            key="source_thumbnails", validator=CollectionThumbnailListValidator, default=[]
        )
        self._playlist_thumbnails = self._validate_key_if_present(
            key="playlist_thumbnails", validator=CollectionThumbnailListValidator, default=[]
        )

    @property
    def url(self) -> OverridesStringFormatterValidator:
        """
        URL to download from, listed in priority from lowest (top) to highest (bottom). If a
        download exists in more than one URL, it will resolve to the bottom-most one and inherit
        those variables.
        """
        return self._url

    @property
    def variables(self) -> DictFormatterValidator:
        """
        Source variables to add to each entry. The top-most collection must define all possible
        variables. Collections below can redefine all of them or a subset of the top-most variables.
        """
        return self._variables

    @property
    def source_thumbnails(self) -> Optional[CollectionThumbnailListValidator]:
        """
        Thumbnails to download from the source, if any exist. The hierarchy is defined as
        source -> playlist -> entry.

        Usage:

        .. code-block:: yaml

           source_thumbnails:
             - name: "poster.jpg"
               uid: "avatar_uncropped"

        UID is the yt-dlp thumbnail ID or can specify ``latest_entry`` to use the last entry's
        thumbnail that was downloaded.
        """
        return self._source_thumbnails

    @property
    def playlist_thumbnails(self) -> Optional[CollectionThumbnailListValidator]:
        """
        Thumbnails to download from the source, if any exist. The hierarchy is defined as
        source -> playlist -> entry.

        Usage:

        .. code-block:: yaml

           playlist_thumbnails:
             - name: "poster.jpg"
               uid: "avatar_uncropped"

        UID is the yt-dlp thumbnail ID or can specify ``latest_entry`` to use the last entry's
        thumbnail that was downloaded.
        """
        return self._playlist_thumbnails


class CollectionUrlListValidator(ListValidator[CollectionUrlValidator]):
    _inner_list_type = CollectionUrlValidator
    _expected_value_type_name = "collection url list"

    def __init__(self, name, value):
        super().__init__(name, value)

        added_variables: Dict[str, str] = self.list[0].variables.dict_with_format_strings

        for idx, collection_url_validator in enumerate(self.list[1:]):
            collection_variables = collection_url_validator.variables.dict_with_format_strings

            # see if this collection contains new added vars (it should not)
            for var in collection_variables.keys():
                if var not in added_variables:
                    raise self._validation_exception(
                        f"Collection url {idx} contains the variable '{var}' that the first "
                        f"collection url does not. The first collection url must define all added "
                        f"variables."
                    )

            # see if this collection is missing any added vars (if so, inherit from the top)
            for var in added_variables.keys():
                if var not in collection_variables.keys():
                    collection_variables[var] = added_variables[var]


class CollectionValidator(StrictDictValidator, AddsVariablesMixin):
    """
    Downloads from multiple URLs. If an entry is returned from more than one URL, it will
    resolve to the bottom-most URL settings.
    """

    _required_keys = {"urls"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate a collection
        """
        if isinstance(value, dict):
            value["urls"] = value.get("urls", [{"url": "placeholder"}])
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)
        self._urls = self._validate_key(key="urls", validator=CollectionUrlListValidator)

    @property
    def collection_urls(self) -> CollectionUrlListValidator:
        """
        Required. The Soundcloud user's url, i.e. ``soundcloud.com/the_username``
        """
        return self._urls

    def added_source_variables(self) -> List[str]:
        """
        Returns
        -------
        List of variables added. The first collection url always contains all the variables.
        """
        return list(self._urls.list[0].variables.keys)

    def validate_with_variables(
        self, source_variables: List[str], override_variables: Dict[str, str]
    ) -> None:
        """
        Ensures new variables added are not existing variables
        """
        for source_var_name in self.added_source_variables():
            if source_var_name in source_variables:
                raise self._validation_exception(
                    f"'{source_var_name}' cannot be used as a variable name because it "
                    f"is an existing source variable"
                )

        base_variables = dict(
            override_variables, **{source_var: "dummy_string" for source_var in source_variables}
        )

        # Apply formatting to each new source variable, ensure it resolves
        for collection_url in self.collection_urls.list:
            for (
                source_var_name,
                source_var_formatter_str,
            ) in collection_url.variables.dict_with_format_strings.items():
                _ = StringFormatterValidator(
                    name=f"{self._name}.{source_var_name}", value=source_var_formatter_str
                ).apply_formatter(base_variables)
