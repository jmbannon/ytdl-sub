from collections import defaultdict
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List

import mediafile

from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.validators.options import OptionsDictValidator
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.audo_codec_validator import AUDIO_CODEC_EXTS
from ytdl_sub.validators.string_formatter_validators import ListFormatterValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator

v: VariableDefinitions = VARIABLES

logger = Logger.get("music-tags")


def _is_multi_field(tag_name: str) -> bool:
    return tag_name in {
        "artists",
        "genres",
        "albumartists",
        "albumtypes",
        "catalognums",
        "languages",
        "artists_credit",
        "artists_sort",
        "albumartists_credit",
        "albumartists_sort",
        "mb_albumartistids",
    }


def _is_date_field(tag_name: str) -> bool:
    return tag_name in {
        "date",
        "original_date",
    }


def _to_datetime(tag_value: str) -> Any:
    return datetime.strptime(tag_value, "%Y-%m-%d")


class MusicTagsOptions(OptionsDictValidator):
    """
    Adds tags to every download audio file using
    `MediaFile <https://mediafile.readthedocs.io/en/latest/>`_,
    the same audio file tagging package used by
    `beets <https://beets.readthedocs.io/en/stable/>`_.
    It supports basic tags like ``title``, ``album``, ``artist`` and ``albumartist``. You can find
    a full list of tags for various file types in MediaFile's
    `source code <https://github.com/beetbox/mediafile/blob/v0.9.0/mediafile.py#L1770>`_.

    Note that the date fields ``date`` and ``original_date`` expected a standardized date in the
    form of YYYY-MM-DD. The variable ``upload_date_standardized`` returns a compatible format.

    :Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           music_tags:
             artist: "{artist}"
             album: "{album}"
             # Supports id3v2.4 multi-tags
             genres:
               - "{genre}"
               - "ytdl-sub"
             albumartists:
               - "{artist}"
               - "ytdl-sub"
             date: "{upload_date_standardized}"
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


class MusicTagsPlugin(Plugin[MusicTagsOptions]):
    plugin_options_type = MusicTagsOptions

    def post_process_entry(self, entry: Entry) -> FileMetadata:
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        if (ext := entry.get(v.ext, str)) not in AUDIO_CODEC_EXTS:
            raise self.plugin_options.validation_exception(
                f"music_tags plugin received a video with the extension '{ext}'. Only audio "
                f"files are supported for setting music tags. Ensure you are converting the video "
                f"to audio using the audio_extract plugin."
            )

        # Resolve the tags into this dict
        tags_to_write: Dict[str, List[str]] = defaultdict(list)
        for tag_name, tag_formatters in self.plugin_options.as_lists.items():
            for tag_formatter in tag_formatters:
                tag_value = self.overrides.apply_formatter(formatter=tag_formatter, entry=entry)
                tags_to_write[tag_name].append(tag_value)

            if _is_date_field(tag_name):
                try:
                    if len(tags_to_write[tag_name]) != 1:
                        raise ValueError("caught below")

                    _ = _to_datetime(tags_to_write[tag_name][0])
                except Exception as exc:
                    raise ValidationException(
                        "Date-based music tags must be a single tag in the form of YYYY-MM-DD"
                    ) from exc

        # write the actual tags if its not a dry run
        if not self.is_dry_run:
            audio_file = mediafile.MediaFile(entry.get_download_file_path())
            for tag_name, tag_value in tags_to_write.items():
                # If the attribute is a date-type, set it as a datetime type
                if _is_date_field(tag_name):
                    setattr(audio_file, tag_name, _to_datetime(tag_value[0]))
                # If the attribute is a multi-type, set it as the list type
                elif _is_multi_field(tag_name):
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

            audio_file.save()

        # report the tags written
        return FileMetadata.from_dict(
            title="Music Tags",
            value_dict=tags_to_write,
        )
