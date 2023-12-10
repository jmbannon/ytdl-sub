import copy
from typing import Any
from typing import Dict

from ytdl_sub.config.plugin import Plugin
from ytdl_sub.config.preset_options import OptionsDictValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.ffmpeg import add_ffmpeg_metadata_key_values
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator

logger = Logger.get("video_tags")


class VideoTagsOptions(OptionsDictValidator):
    """
    Adds tags to every downloaded video file using ffmpeg ``-metadata key=value`` args.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           video_tags:
             title: "{title}"
             date: "{upload_date}"
             description: "{description}"
    """

    _optional_keys = {"tags"}
    _allow_extra_keys = True

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

        new_tags_dict: Dict[str, Any] = copy.deepcopy(value)
        old_tags_dict = new_tags_dict.pop("tags", {})

        self._is_old_format = len(old_tags_dict) > 0
        self._tags = DictFormatterValidator(name=name, value=dict(old_tags_dict, **new_tags_dict))

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
        # pylint: disable=protected-access
        if self.plugin_options._is_old_format:
            logger.warning(
                "video_tags.tags is now deprecated. Place your tags directly under video_tags "
                "instead. The old format will be removed in October of 2023. See "
                "https://ytdl-sub.readthedocs.io/en/latest/deprecation_notices.html#video-tags "
                "for more details."
            )

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
