from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.string_select_validator import StringSelectValidator
from ytdl_sub.validators.validators import BoolValidator
from ytdl_sub.validators.validators import StringListValidator

SUBTITLE_EXTENSIONS: Set[str] = {"srt", "vtt", "ass", "lrc"}


class SubtitlesTypeValidator(StringSelectValidator):
    _expected_value_type_name = "subtitles type"
    _select_values = SUBTITLE_EXTENSIONS


class SubtitleOptions(StrictDictValidator):
    """
    Defines how to download and store subtitles.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           subtitle_options:
             # required
             output_directory: "/path/to/videos_or_music"
             file_name: "{title_sanitized}.{ext}"
             # optional
             thumbnail_name: "{title_sanitized}.{thumbnail_ext}"
             maintain_download_archive: True
             keep_files_before: now
             keep_files_after: 19000101
    """

    _optional_keys = {
        "subtitles_name",
        "subtitles_type",
        "embed_subtitles",
        "languages",
        "allow_auto_generated_subtitles",
    }

    def __init__(self, name, value):
        super().__init__(name, value)
        self._subtitles_name = self._validate_key_if_present(
            key="subtitles_name", validator=StringFormatterValidator
        )
        self._subtitles_type = self._validate_key_if_present(
            key="subtitles_type", validator=SubtitlesTypeValidator, default="srt"
        )
        self._embed_subtitles = self._validate_key_if_present(
            key="embed_subtitles", validator=BoolValidator
        )
        self._languages = self._validate_key_if_present(
            key="languages", validator=StringListValidator, default=["en"]
        ).list
        self._allow_auto_generated_subtitles = self._validate_key_if_present(
            key="allow_auto_generated_subtitles", validator=BoolValidator, default=False
        ).value

    @property
    def subtitles_name(self) -> Optional[StringFormatterValidator]:
        """
        Optional. The file name for the media's subtitles if they are present. This can include
        directories such as ``"Season {upload_year}/{title}.{subtitle_ext}"``, and will be placed
        in the output directory.
        """
        return self._subtitles_name

    @property
    def subtitles_type(self) -> Optional[str]:
        """
        Optional. The subtitles file format. Defaults to ``srt``
        """
        return self._subtitles_type

    @property
    def embed_subtitles(self) -> Optional[bool]:
        """
        Optional. Whether to embed the subtitles into the video file.
        """
        return self._subtitles_type

    @property
    def languages(self) -> Optional[List[str]]:
        """
        Optional. Language(s) to download for subtitles. Defaults to ``en``
        """
        return [lang.value for lang in self._languages]

    @property
    def allow_auto_generated_subtitles(self) -> Optional[bool]:
        """
        Optional. Whether to allow auto generated subtitles. Defaults to False.
        """
        return self._allow_auto_generated_subtitles


class SubtitlesPlugin(Plugin[SubtitleOptions]):
    plugin_options_type = SubtitleOptions

    def ytdl_options(self) -> Optional[Dict]:
        ytdl_options_builder = YTDLOptionsBuilder()

        write_subtitle_file: bool = self.plugin_options.subtitles_name is not None
        if write_subtitle_file:
            ytdl_options_builder.add(
                {
                    "writesubtitles": True,
                    "postprocessors": {
                        "key": "FFmpegSubtitlesConvertor",
                        "format": self.plugin_options.subtitles_type,
                    },
                }
            )

        if self.plugin_options.embed_subtitles:
            ytdl_options_builder.add(
                {
                    "postprocessors": [
                        # already_have_subtitle=True means keep the subtitle files
                        {"key": "FFmpegEmbedSubtitle", "already_have_subtitle": write_subtitle_file}
                    ]
                }
            )

        # If neither subtitles_name or embed_subtitles is set, do not set any other flags
        if not ytdl_options_builder.to_dict():
            return {}

        return ytdl_options_builder.add(
            {
                "writeautomaticsub": self.plugin_options.allow_auto_generated_subtitles,
                "subtitleslangs": self.plugin_options.languages,
            }
        ).to_dict()

    def post_process_entry(self, entry: Entry) -> None:
        """
        Creates an entry's NFO file using values defined in the metadata options

        Parameters
        ----------
        entry:
            Entry to create an NFO file for
        """

        # def get_ytdlp_download_subtitle_paths(self) -> List[str]:
        #     possible_subtitle_exts = SUBTITLE_EXTENSIONS
        #     subtitle_paths: List[str] = []
        #
        #     for ext in possible_subtitle_exts:
        #         for path in Path(self.working_directory()).rglob("*"):
        #             if (
        #                     path.is_file()
        #                     and path.name.startswith(self.uid)
        #                     and path.name.endswith(f".{ext}")
        #             ):
        #                 subtitle_paths.append(str(path))
        #
        #     return subtitle_paths
