import copy
from abc import ABC
from typing import Any
from typing import Dict
from typing import Type

from ytdl_subscribe.downloaders.downloader import DownloaderValidator
from ytdl_subscribe.downloaders.soundcloud_downloader import (
    SoundcloudAlbumsAndSinglesDownloadOptions,
)
from ytdl_subscribe.downloaders.youtube_downloader import YoutubeChannelDownloaderOptions
from ytdl_subscribe.downloaders.youtube_downloader import YoutubePlaylistDownloaderOptions
from ytdl_subscribe.downloaders.youtube_downloader import YoutubeVideoDownloaderOptions
from ytdl_subscribe.validators.strict_dict_validator import StrictDictValidator
from ytdl_subscribe.validators.validators import StringValidator


class DownloadStrategyValidator(StrictDictValidator, ABC):
    """
    Validates the download strategy of a source. Does not validate the source options.
    """

    # All media sources must define a download strategy
    _required_keys = {"download_strategy"}

    # Extra fields will be strict-validated using other StictDictValidators
    _allow_extra_keys = True

    _download_strategy_to_source_mapping: Dict[str, Type[DownloaderValidator]] = {}

    def __init__(self, name: str, value: Any):
        super().__init__(name=name, value=value)
        download_strategy_name = self._validate_key(
            key="download_strategy",
            validator=StringValidator,
        ).value

        if download_strategy_name not in self._possible_download_strategies:
            raise self._validation_exception(
                f"download_strategy must be one of the following: "
                f"{', '.join(self._possible_download_strategies)}"
            )

        # Remove the 'download_strategy' key before passing the other keys to the actual
        # source validator
        source_validator_dict = copy.deepcopy(self._dict)
        del source_validator_dict["download_strategy"]

        source_validator_class = self._download_strategy_to_source_mapping[download_strategy_name]
        self.source_validator = source_validator_class(name=self._name, value=source_validator_dict)

    @property
    def _possible_download_strategies(self):
        return sorted(list(self._download_strategy_to_source_mapping.keys()))


class SoundcloudDownloadStrategyValidator(DownloadStrategyValidator):
    _download_strategy_to_source_mapping = {
        "albums_and_singles": SoundcloudAlbumsAndSinglesDownloadOptions
    }


class YoutubeDownloadStrategyValidator(DownloadStrategyValidator):
    _download_strategy_to_source_mapping = {
        "channel": YoutubeChannelDownloaderOptions,
        "playlist": YoutubePlaylistDownloaderOptions,
        "video": YoutubeVideoDownloaderOptions,
    }
