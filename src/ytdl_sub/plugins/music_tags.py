from typing import Dict

import mediafile

from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.validators import StringValidator


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
               genre: "ytdl downloaded music"
    """

    _required_keys = {"tags"}
    _optional_keys = {"multi_value_separator"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self._tags = self._validate_key(key="tags", validator=DictFormatterValidator)

        self.multi_value_separator = self._validate_key_if_present(
            key="multi_value_separator", validator=StringValidator
        )

    @property
    def tags(self) -> DictFormatterValidator:
        """
        Key/values of tag names/tag values. Supports source and override variables.
        """
        return self._tags


class MusicTagsPlugin(Plugin[MusicTagsOptions]):
    plugin_options_type = MusicTagsOptions

    def post_process_entry(self, entry: Entry) -> FileMetadata:
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        supported_fields = list(mediafile.MediaFile.sorted_fields())
        tags_to_write: Dict[str, str] = {}
        for tag_name, tag_formatter in self.plugin_options.tags.dict.items():
            if tag_name not in supported_fields:
                # TODO: Add support for custom fields
                self._logger.warning(
                    "tag '%s' is not supported for %s files. Supported tags: %s",
                    tag_name,
                    entry.ext,
                    ", ".join(sorted(supported_fields)),
                )
                continue

            tag_value = self.overrides.apply_formatter(formatter=tag_formatter, entry=entry)
            tags_to_write[tag_name] = tag_value

        # write the actual tags if its not a dry run
        if not self.is_dry_run:
            audio_file = mediafile.MediaFile(entry.get_download_file_path())
            for tag_name, tag_value in tags_to_write.items():
                setattr(audio_file, tag_name, tag_value)
            audio_file.save()

        # report the tags written
        return FileMetadata.from_dict(value_dict=tags_to_write, title="Music Tags")
