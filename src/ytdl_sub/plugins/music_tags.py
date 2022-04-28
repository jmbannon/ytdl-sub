import mediafile

from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.validators.string_formatter_validators import DictFormatterValidator
from ytdl_sub.validators.validators import StringValidator


class MusicTagsOptions(PluginOptions):
    _required_keys = {"tags"}
    _optional_keys = {"multi_value_separator"}

    def __init__(self, name, value):
        super().__init__(name, value)

        self.tags = self._validate_key(key="tags", validator=DictFormatterValidator)

        self.multi_value_separator = self._validate_key_if_present(
            key="multi_value_separator", validator=StringValidator
        )


class MusicTagsPlugin(Plugin[MusicTagsOptions]):
    plugin_options_type = MusicTagsOptions

    def post_process_entry(self, entry: Entry):
        """
        Tags the entry's audio file using values defined in the metadata options
        """
        audio_file = mediafile.MediaFile(entry.get_download_file_path())
        for tag, tag_formatter in self.plugin_options.tags.dict.items():
            if tag not in audio_file.fields():
                # TODO: Add proper logger and warn here
                print(
                    f"[ytld-sub: WARN] tag {tag} is not supported for {entry.ext} files. Supported "
                    f"tags: {', '.join(audio_file.sorted_fields())}"
                )

            tag_value = self.overrides.apply_formatter(formatter=tag_formatter, entry=entry)
            setattr(audio_file, tag, tag_value)

        audio_file.save()
