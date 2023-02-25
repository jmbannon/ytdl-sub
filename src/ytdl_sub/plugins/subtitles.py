from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.utils.logger import Logger
from ytdl_sub.validators.file_path_validators import StringFormatterFilePathValidator
from ytdl_sub.validators.string_formatter_validators import StringFormatterValidator
from ytdl_sub.validators.string_select_validator import StringSelectValidator
from ytdl_sub.validators.validators import BoolValidator
from ytdl_sub.validators.validators import StringListValidator

SUBTITLE_EXTENSIONS: Set[str] = {"srt", "vtt", "ass", "lrc"}


logger = Logger.get(name="subtitles")


class SubtitlesTypeValidator(StringSelectValidator):
    _expected_value_type_name = "subtitles type"
    _select_values = SUBTITLE_EXTENSIONS


class SubtitleOptions(PluginOptions):
    """
    Defines how to download and store subtitles. Using this plugin creates two new variables:
    ``lang`` and ``subtitles_ext``. ``lang`` is dynamic since you can download multiple subtitles.
    It will set the respective language to the correct subtitle file.

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           subtitles:
             subtitles_name: "{title_sanitized}.{lang}.{subtitles_ext}"
             subtitles_type: "srt"
             embed_subtitles: False
             languages: "en"  # supports list of multiple languages
             allow_auto_generated_subtitles: False
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
            key="subtitles_name", validator=StringFormatterFilePathValidator
        )
        self._subtitles_type = self._validate_key_if_present(
            key="subtitles_type", validator=SubtitlesTypeValidator, default="srt"
        ).value
        self._embed_subtitles = self._validate_key_if_present(
            key="embed_subtitles",
            validator=BoolValidator,
            default=False,
        ).value
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
        directories such as ``"Season {upload_year}/{title_sanitized}.{lang}.{subtitles_ext}"``, and
        will be placed in the output directory. ``lang`` is dynamic since you can download multiple
        subtitles. It will set the respective language to the correct subtitle file.
        """
        return self._subtitles_name

    @property
    def subtitles_type(self) -> Optional[str]:
        """
        Optional. One of the subtitle file types "srt", "vtt", "ass", "lrc". Defaults to "srt"
        """
        return self._subtitles_type

    @property
    def embed_subtitles(self) -> Optional[bool]:
        """
        Optional. Whether to embed the subtitles into the video file. Defaults to False.
        NOTE: webm files can only embed "vtt" subtitle types.
        """
        return self._embed_subtitles

    @property
    def languages(self) -> Optional[List[str]]:
        """
        Optional. Language code(s) to download for subtitles. Supports a single or list of multiple
        language codes. Defaults to "en".
        """
        return [lang.value for lang in self._languages]

    @property
    def allow_auto_generated_subtitles(self) -> Optional[bool]:
        """
        Optional. Whether to allow auto generated subtitles. Defaults to False.
        """
        return self._allow_auto_generated_subtitles

    def added_source_variables(self) -> List[str]:
        """
        Returns
        -------
        List of new source variables created by using the subtitles plugin
        """
        return ["lang", "subtitles_ext"]


class SubtitlesPlugin(Plugin[SubtitleOptions]):
    plugin_options_type = SubtitleOptions

    def ytdl_options(self) -> Optional[Dict]:
        builder = YTDLOptionsBuilder().add({"writesubtitles": True})

        if self.plugin_options.embed_subtitles:
            builder.add(
                {"postprocessors": [{"key": "FFmpegEmbedSubtitle", "already_have_subtitle": True}]}
            )

        if self.plugin_options.subtitles_name:
            builder.add(
                {
                    "postprocessors": [
                        {
                            "key": "FFmpegSubtitlesConvertor",
                            "format": self.plugin_options.subtitles_type,
                        }
                    ],
                }
            )

        # If neither subtitles_name or embed_subtitles is set, do not set any other flags
        if not builder.to_dict():
            return {}

        builder.add(
            {
                "writeautomaticsub": self.plugin_options.allow_auto_generated_subtitles,
                "subtitleslangs": self.plugin_options.languages,
            }
        )

        return builder.to_dict()

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        if not (requested_subtitles := entry.kwargs_get("requested_subtitles", None)):
            return entry

        languages = sorted(requested_subtitles.keys())
        entry.add_variables(
            variables_to_add={
                "subtitles_ext": self.plugin_options.subtitles_type,
                "lang": ",".join(languages),
            }
        )

        return entry

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        """
        Creates an entry's NFO file using values defined in the metadata options

        Parameters
        ----------
        entry:
            Entry to create subtitles for
        """
        requested_subtitles = entry.kwargs("requested_subtitles")
        if not requested_subtitles:
            logger.info("subtitles not found for %s", entry.title)
            return None

        file_metadata: Optional[FileMetadata] = None
        langs = list(requested_subtitles.keys())

        if self.plugin_options.embed_subtitles:
            file_metadata = FileMetadata(f"Embedded subtitles with lang(s) {', '.join(langs)}")
        if self.plugin_options.subtitles_name:
            for lang in langs:
                subtitle_file_name = f"{entry.uid}.{lang}.{self.plugin_options.subtitles_type}"
                output_subtitle_file_name = self.overrides.apply_formatter(
                    formatter=self.plugin_options.subtitles_name,
                    entry=entry,
                    function_overrides={"lang": lang},
                )

                self.save_file(
                    file_name=subtitle_file_name,
                    output_file_name=output_subtitle_file_name,
                    entry=entry,
                )

        # Delete any possible original subtitle files before conversion
        # Can happen for both file and embedded subs
        for lang in langs:
            for possible_ext in SUBTITLE_EXTENSIONS:
                possible_subs_file = (
                    Path(self.working_directory) / f"{entry.uid}.{lang}.{possible_ext}"
                )
                FileHandler.delete(possible_subs_file)

        return file_metadata
