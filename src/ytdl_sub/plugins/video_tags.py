from typing import Any
from typing import Dict

from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.ffmpeg import add_ffmpeg_metadata_key_values
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator


class VideoTagsOptions(PluginOptions):
    """
    Adds tags to every downloaded video file using ffmpeg ``-metadata key=value`` args.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           video_tags:
             tags:
               title: "{title}"
               date: "{upload_date}"
               description: "{description}"
    """

    _required_keys = {"tags"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate video tags
        """
        if isinstance(value, dict):
            value["tags"] = value.get("tags", {})
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)
        self._tags = self._validate_key(key="tags", validator=DictFormatterValidator)

    @property
    def tags(self) -> DictFormatterValidator:
        """
        Key/values of tag names/values. Supports source and override variables.
        """
        return self._tags


class VideoTagsPlugin(Plugin[VideoTagsOptions]):
    plugin_options_type = VideoTagsOptions

    def post_process_entry(self, entry: Entry) -> FileMetadata:
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        tags_to_write: Dict[str, str] = {}
        for tag_name, tag_formatter in self.plugin_options.tags.dict.items():
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
