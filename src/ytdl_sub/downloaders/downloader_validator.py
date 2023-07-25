import abc
from abc import ABC
from typing import Dict
from typing import List
from typing import TypeVar

from ytdl_sub.config.preset_options import OptionsValidator
from ytdl_sub.downloaders.url.validators import MultiUrlValidator


class DownloaderValidator(OptionsValidator, ABC):
    """
    Placeholder class to define downloader options
    """

    @property
    @abc.abstractmethod
    def collection_validator(self) -> MultiUrlValidator:
        """
        Returns
        -------
        MultiUrlValidator
            To determine how the entries are downloaded
        """

    def added_source_variables(self) -> List[str]:
        """
        Returns
        -------
        Added source variables on the collection
        """
        return self.collection_validator.added_source_variables()

    def validate_with_variables(
        self, source_variables: List[str], override_variables: Dict[str, str]
    ) -> None:
        """
        Validates any source variables added by the collection
        """
        self.collection_validator.validate_with_variables(
            source_variables=source_variables, override_variables=override_variables
        )


TDownloaderValidator = TypeVar("TDownloaderValidator", bound=DownloaderValidator)
