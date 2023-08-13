import copy
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.config.preset_options import OptionsValidator
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.string_formatter_validators import OverridesStringFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import BoolValidator
from ytdl_sub.validators.validators import ListValidator


class UrlThumbnailValidator(StrictDictValidator):
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


class UrlThumbnailListValidator(ListValidator[UrlThumbnailValidator]):
    _inner_list_type = UrlThumbnailValidator


class UrlValidator(StrictDictValidator):
    _required_keys = {"url"}
    _optional_keys = {"variables", "source_thumbnails", "playlist_thumbnails", "download_reverse"}

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
            key="source_thumbnails", validator=UrlThumbnailListValidator, default=[]
        )
        self._playlist_thumbnails = self._validate_key_if_present(
            key="playlist_thumbnails", validator=UrlThumbnailListValidator, default=[]
        )
        self._download_reverse = self._validate_key(
            key="download_reverse", validator=BoolValidator, default=True
        )

    @property
    def url(self) -> OverridesStringFormatterValidator:
        """
        Required. URL to download from.
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
    def playlist_thumbnails(self) -> Optional[UrlThumbnailListValidator]:
        """
        Thumbnails to download from the playlist, if any exist. Playlist is the ``yt-dlp`` naming
        convention for a set that contains multiple entries. For example, the URL
        ``https://www.youtube.com/c/RickastleyCoUkOfficial`` would have ``playlist`` refer to the
        channel.

        Usage:

        .. code-block:: yaml

           playlist_thumbnails:
             - name: "poster.jpg"
               uid: "avatar_uncropped"
             - name: "fanart.jpg"
               uid: "banner_uncropped"

        ``name`` is the file name relative to the output directory to store the thumbnail.
        ``uid`` is the yt-dlp thumbnail ID. Can specify ``latest_entry`` to use the latest entry's
        thumbnail.
        """
        return self._playlist_thumbnails

    @property
    def source_thumbnails(self) -> Optional[UrlThumbnailListValidator]:
        """
        Thumbnails to download from the source, if any exist. Source in this context refers to the
        set of sets. For example, the URL
        ``https://www.youtube.com/c/RickastleyCoUkOfficial/playlists``
        would have ``playlist`` refer to each individual playlist, whereas ``source`` refers
        to the channel.

        Usage:

        .. code-block:: yaml

           source_thumbnails:
             - name: "poster.jpg"
               uid: "avatar_uncropped"
             - name: "fanart.jpg"
               uid: "banner_uncropped"

        ``name`` is the file name relative to the output directory to store the thumbnail.
        ``uid`` is the yt-dlp thumbnail ID. Can specify ``latest_entry`` to use the latest entry's
        thumbnail.
        """
        return self._source_thumbnails

    @property
    def download_reverse(self) -> bool:
        """
        Optional. Whether to download entries in the reverse order of the metadata downloaded.
        Defaults to True.
        """
        return self._download_reverse.value


class UrlStringOrDictValidator(UrlValidator):
    """
    URL validator that supports a single string like:

    download:
      - "https://"

    or

    download:
      - url: "https://"
    """

    _expected_value_type = (dict, str)

    def __init__(self, name, value):
        super().__init__(name, {"url": value} if isinstance(value, str) else value)


class UrlListValidator(ListValidator[UrlStringOrDictValidator]):
    _inner_list_type = UrlStringOrDictValidator
    _expected_value_type_name = "collection url list"

    def __init__(self, name, value):
        super().__init__(name, value)

        added_variables: Dict[str, str] = self.list[0].variables.dict_with_format_strings

        for idx, url_validator in enumerate(self.list[1:]):
            collection_variables = url_validator.variables.dict_with_format_strings

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


class MultiUrlValidator(OptionsValidator):
    """
    Downloads from multiple URLs. If an entry is returned from more than one URL, it will
    resolve to the bottom-most URL settings.
    """

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate a collection
        """
        if isinstance(value, dict):
            value["url"] = value.get("url", "sadfasdf")
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)

        # Copy since we're popping things
        value_copy = copy.deepcopy(value)
        if isinstance(value, dict):
            # Pop old required field in case it's still there
            value_copy.pop("download_strategy", None)

        # Deal with old multi-url download strategy
        if isinstance(value, dict) and "urls" in value_copy:
            self._urls = UrlListValidator(name=name, value=value_copy["urls"])
        else:
            self._urls = UrlListValidator(name=name, value=value_copy)

    @property
    def urls(self) -> UrlListValidator:
        """
        Required. A list of :ref:`url` with the addition of the ``variables`` attribute.
        Multiple URLs should be listed in the order of priority, with the lowest priority being the
        top-most, and highest priority being the bottom-most. If a download exists in more than
        one URL, it will resolve to the bottom-most one (the highest priority) and
        inherit those variables.
        """
        return self._urls

    @property
    def variables(self) -> DictFormatterValidator:
        """
        Optional. Source variables to add to each entry downloaded from its respective :ref:`url`.
        The top-most :ref:`url` must define all possible variables. Other :ref:`url` entries can
        redefine all of them or a subset of the top-most variables.
        """
        # keep for readthedocs documentation
        return self._urls.list[0].variables

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
        for collection_url in self.urls.list:
            for (
                source_var_name,
                source_var_formatter_str,
            ) in collection_url.variables.dict_with_format_strings.items():
                _ = StringFormatterValidator(
                    name=f"{self._name}.{source_var_name}", value=source_var_formatter_str
                ).apply_formatter(base_variables)

        # Ensure at least URL is non-empty
        has_non_empty_url = False
        for url_validator in self.urls.list:
            has_non_empty_url |= bool(url_validator.url.apply_formatter(override_variables))

        if not has_non_empty_url:
            raise self._validation_exception("Must contain at least one url that is non-empty")
