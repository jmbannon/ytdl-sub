from collections import defaultdict
from typing import Any
from typing import Dict
from typing import List

import mediafile

from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.thumbnail import convert_download_thumbnail
from ytdl_sub.validators.audo_codec_validator import AUDIO_CODEC_EXTS
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import ListFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.validators import BoolValidator

logger = Logger.get("music_tags")


class MusicTagsValidator(StrictDictValidator):
    """
    Validator for the music_tag's `tags` field. Treat each value as a list.
    Can still specify it like a single value but under-the-hood it's a list of a single element.
    """

    _optional_keys = set(list(mediafile.MediaFile.sorted_fields()))

    def __init__(self, name, value):
        super().__init__(name, value)

        self._tags: Dict[str, List[StringFormatterValidator]] = {}
        for key in self._keys:
            self._tags[key] = self._validate_key(key=key, validator=ListFormatterValidator).list

    @property
    def as_lists(self) -> Dict[str, List[StringFormatterValidator]]:
        """
        Returns
        -------
        Tag formatter(s) as a list
        """
        return self._tags


class MusicTagsOptions(PluginOptions):
    """
    Adds tags to every download audio file using
    `MediaFile <https://mediafile.readthedocs.io/en/latest/>`_,
    the same audio file tagging package used by
    `beets <https://beets.readthedocs.io/en/stable/>`_.
    It supports basic tags like ``title``, ``album``, ``artist`` and ``albumartist``. You can find
    a full list of tags for various file types in MediaFile's
    `source code <https://github.com/beetbox/mediafile/blob/v0.9.0/mediafile.py#L1770>`_.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           music_tags:
             tags:
               artist: "{artist}"
               album: "{album}"
               genre: "ytdl-sub"
               # Supports id3v2.4 multi-tags
               albumartists:
                 - "{artist}"
                 - "ytdl-sub"
             # Optional
             embed_thumbnail: False
    """

    _required_keys = {"tags"}
    _optional_keys = {"embed_thumbnail"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate music tags
        """
        if isinstance(value, dict):
            value["tags"] = value.get("tags", {})
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)

        self._tags = self._validate_key(key="tags", validator=MusicTagsValidator)
        self._embed_thumbnail = self._validate_key_if_present(
            key="embed_thumbnail", validator=BoolValidator, default=False
        ).value

    @property
    def tags(self) -> MusicTagsValidator:
        """
        Key, values of tag names, tag values. Supports source and override variables.
        Supports lists which will get written to MP3s as id3v2.4 multi-tags.
        """
        return self._tags

    @property
    def embed_thumbnail(self) -> bool:
        """
        Optional. Whether to embed the thumbnail into the audio file.
        """
        return self._embed_thumbnail


class MusicTagsPlugin(Plugin[MusicTagsOptions]):
    plugin_options_type = MusicTagsOptions

    def post_process_entry(self, entry: Entry) -> FileMetadata:
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        if entry.ext not in AUDIO_CODEC_EXTS:
            raise self.plugin_options.validation_exception(
                f"music_tags plugin received a video with the extension '{entry.ext}'. Only audio "
                f"files are supported for setting music tags. Ensure you are converting the video "
                f"to audio using the audio_extract plugin."
            )

        # Resolve the tags into this dict
        tags_to_write: Dict[str, List[str]] = defaultdict(list)
        for tag_name, tag_formatters in self.plugin_options.tags.as_lists.items():
            for tag_formatter in tag_formatters:
                tag_value = self.overrides.apply_formatter(formatter=tag_formatter, entry=entry)
                tags_to_write[tag_name].append(tag_value)

        # write the actual tags if its not a dry run
        if not self.is_dry_run:
            audio_file = mediafile.MediaFile(entry.get_download_file_path())
            for tag_name, tag_value in tags_to_write.items():
                # If the attribute is a List-type, set it as the list type
                if isinstance(getattr(audio_file, tag_name), list):
                    setattr(audio_file, tag_name, tag_value)
                # Otherwise, set as single value
                else:
                    if len(tag_value) > 1:
                        logger.warning(
                            "Music tag '%s' does not support lists. "
                            "Only setting the first element",
                            tag_name,
                        )
                    setattr(audio_file, tag_name, tag_value[0])

            if self.plugin_options.embed_thumbnail:
                # convert the entry thumbnail so it is embedded as jpg
                convert_download_thumbnail(entry=entry)

                with open(entry.get_download_thumbnail_path(), "rb") as thumb:
                    mediafile_img = mediafile.Image(
                        data=thumb.read(), desc="cover", type=mediafile.ImageType.front
                    )

                audio_file.images = [mediafile_img]

            audio_file.save()

        # report the tags written
        title = f"{'Embedded Thumbnail, ' if self.plugin_options.embed_thumbnail else ''}Music Tags"
        return FileMetadata.from_dict(
            value_dict=tags_to_write,
            title=title,
        )
