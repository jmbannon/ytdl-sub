from typing import Dict

from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.validators.options import OptionsValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.ffmpeg import add_ffmpeg_metadata_key_values
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator

logger = Logger.get("video-tags")


class VideoTagsOptions(DictFormatterValidator, OptionsValidator):
    """
    Adds tags to every downloaded video file using ffmpeg ``-metadata key=value`` args.

    :Usage:

    .. code-block:: yaml

       video_tags:
         title: "{title}"
         date: "{upload_date}"
         description: "{description}"
    """


class VideoTagsPlugin(Plugin[VideoTagsOptions]):
    plugin_options_type = VideoTagsOptions

    def post_process_entry(self, entry: Entry) -> FileMetadata:
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        tags_to_write: Dict[str, str] = {}
        for tag_name, tag_formatter in self.plugin_options.dict.items():
            tag_value = self.overrides.apply_formatter(formatter=tag_formatter, entry=entry)
            tags_to_write[tag_name] = tag_value

        # write the actual tags if its not a dry run
        if not self.is_dry_run:
            add_ffmpeg_metadata_key_values(
                file_path=entry.get_download_file_path(),
                key_values=tags_to_write,
            )

        # report the tags written
        return FileMetadata.from_dict(value_dict=tags_to_write, title="Video Tags")
