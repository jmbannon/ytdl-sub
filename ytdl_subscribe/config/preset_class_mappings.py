from typing import Dict
from typing import List
from typing import Type

from ytdl_subscribe.downloaders.downloader import Downloader
from ytdl_subscribe.downloaders.soundcloud_downloader import SoundcloudAlbumsAndSinglesDownloader
from ytdl_subscribe.downloaders.youtube_downloader import YoutubeChannelDownloader
from ytdl_subscribe.downloaders.youtube_downloader import YoutubePlaylistDownloader
from ytdl_subscribe.downloaders.youtube_downloader import YoutubeVideoDownloader
from ytdl_subscribe.plugins.convert_thumbnail import ConvertThumbnailPlugin
from ytdl_subscribe.plugins.music_tags import MusicTagsPlugin
from ytdl_subscribe.plugins.nfo_tags import NfoTagsPlugin
from ytdl_subscribe.plugins.output_directory_nfo_tags import OutputDirectoryNfoTagsPlugin
from ytdl_subscribe.plugins.plugin import Plugin


class DownloadStrategyMapping:
    """
    Maps downloader strategies defined in the preset to its respective downloader class
    """

    _MAPPING: Dict[str, Dict[str, Type[Downloader]]] = {
        "youtube": {
            "video": YoutubeVideoDownloader,
            "playlist": YoutubePlaylistDownloader,
            "channel": YoutubeChannelDownloader,
        },
        "soundcloud": {
            "albums and singles": SoundcloudAlbumsAndSinglesDownloader,
        },
    }

    @classmethod
    def sources(cls) -> List[str]:
        """
        Returns
        -------
        Available download sources
        """
        return sorted(list(cls._MAPPING.keys()))

    @classmethod
    def _validate_is_source(cls, source: str) -> None:
        """
        Ensure the source exists
        """
        if source not in cls.sources():
            raise ValueError(f"Tried to use source '{source}' that does not exist")

    @classmethod
    def source_download_strategies(cls, source: str) -> List[str]:
        """
        Parameters
        ----------
        source
            Name of the source

        Returns
        -------
        Available download strategies for the given source
        """
        cls._validate_is_source(source)
        return sorted(list(cls._MAPPING[source].keys()))

    @classmethod
    def _validate_is_download_strategy(cls, source: str, download_strategy: str) -> None:
        """
        Ensure the download strategy for the given source exists
        """
        if download_strategy not in cls.source_download_strategies(source):
            raise ValueError(
                f"Tried to use download strategy '{download_strategy}' with source '{source}', "
                f"which does not exist"
            )

    @classmethod
    def get(cls, source: str, download_strategy: str) -> Type[Downloader]:
        cls._validate_is_download_strategy(source, download_strategy)
        return cls._MAPPING[source][download_strategy]


class PluginMapping:
    """
    Maps plugins defined in the preset to its respective plugin class
    """

    _MAPPING: Dict[str, Type[Plugin]] = {
        "convert_thumbnail": ConvertThumbnailPlugin,
        "music_tags": MusicTagsPlugin,
        "nfo_tags": NfoTagsPlugin,
        "output_directory_nfo_tags": OutputDirectoryNfoTagsPlugin,
    }

    @classmethod
    def plugins(cls) -> List[str]:
        """
        Returns
        -------
        Available download sources
        """
        return sorted(list(cls._MAPPING.keys()))

    @classmethod
    def get(cls, plugin: str) -> Type[Plugin]:
        if plugin not in cls.plugins():
            raise ValueError(f"Tried to use plugin '{plugin}' that does not exist")
        return cls._MAPPING[plugin]
