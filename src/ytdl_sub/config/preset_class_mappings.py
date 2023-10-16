from typing import Dict
from typing import List
from typing import Type

from ytdl_sub.config.plugin import Plugin
from ytdl_sub.plugins.audio_extract import AudioExtractPlugin
from ytdl_sub.plugins.chapters import ChaptersPlugin
from ytdl_sub.plugins.date_range import DateRangePlugin
from ytdl_sub.plugins.embed_thumbnail import EmbedThumbnailPlugin
from ytdl_sub.plugins.file_convert import FileConvertPlugin
from ytdl_sub.plugins.format import FormatPlugin
from ytdl_sub.plugins.internal.view import ViewPlugin
from ytdl_sub.plugins.match_filters import MatchFiltersPlugin
from ytdl_sub.plugins.music_tags import MusicTagsPlugin
from ytdl_sub.plugins.nfo_tags import NfoTagsPlugin
from ytdl_sub.plugins.output_directory_nfo_tags import OutputDirectoryNfoTagsPlugin
from ytdl_sub.plugins.regex import RegexPlugin
from ytdl_sub.plugins.split_by_chapters import SplitByChaptersPlugin
from ytdl_sub.plugins.subtitles import SubtitlesPlugin
from ytdl_sub.plugins.video_tags import VideoTagsPlugin


class PluginMapping:
    """
    Maps plugins defined in the preset to its respective plugin class
    """

    _MAPPING: Dict[str, Type[Plugin]] = {
        "_view": ViewPlugin,
        "audio_extract": AudioExtractPlugin,
        "date_range": DateRangePlugin,
        "embed_thumbnail": EmbedThumbnailPlugin,
        "file_convert": FileConvertPlugin,
        "format": FormatPlugin,
        "match_filters": MatchFiltersPlugin,
        "music_tags": MusicTagsPlugin,
        "video_tags": VideoTagsPlugin,
        "nfo_tags": NfoTagsPlugin,
        "output_directory_nfo_tags": OutputDirectoryNfoTagsPlugin,
        "regex": RegexPlugin,
        "subtitles": SubtitlesPlugin,
        "chapters": ChaptersPlugin,
        "split_by_chapters": SplitByChaptersPlugin,
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
        """
        Parameters
        ----------
        plugin
            Name of the plugin

        Returns
        -------
        The plugin class

        Raises
        ------
        ValueError
            Raised if the plugin does not exist
        """
        if plugin not in cls.plugins():
            raise ValueError(
                f"Tried to use plugin '{plugin}' that does not exist. Available plugins: "
                f"{', '.join(cls.plugins())}"
            )
        return cls._MAPPING[plugin]
