import music_tag

from ytdl_subscribe.entries.entry import Entry
from ytdl_subscribe.plugins.plugin import Plugin
from ytdl_subscribe.plugins.plugin import PluginOptions
from ytdl_subscribe.validators.string_formatter_validators import DictFormatterValidator
from ytdl_subscribe.validators.validators import StringValidator


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
        audio_file = music_tag.load_file(entry.get_download_file_path())
        for tag, tag_formatter in self.plugin_options.tags.dict.items():
            audio_file[tag] = self.overrides.apply_formatter(formatter=tag_formatter, entry=entry)
        audio_file.save()
