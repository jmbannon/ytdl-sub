import os.path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set

from ytdl_sub.config.plugin.plugin import Plugin
from ytdl_sub.config.plugin.plugin_operation import PluginOperation
from ytdl_sub.config.validators.options import ToggleableOptionsDictValidator
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions
from ytdl_sub.utils.exceptions import FileNotDownloadedException
from ytdl_sub.utils.file_handler import FileMetadata
from ytdl_sub.validators.audo_codec_validator import AUDIO_CODEC_EXTS
from ytdl_sub.validators.audo_codec_validator import AUDIO_CODEC_TYPES_EXTENSION_MAPPING
from ytdl_sub.validators.audo_codec_validator import AudioTypeValidator
from ytdl_sub.validators.validators import FloatValidator

v: VariableDefinitions = VARIABLES


class AudioExtractOptions(ToggleableOptionsDictValidator):
    """
    Extracts audio from a video file.

    :Usage:

    .. code-block:: yaml

       audio_extract:
         codec: "mp3"
         quality: 128
    """

    _required_keys = {"codec"}
    _optional_keys = {"enable", "quality"}

    @classmethod
    def partial_validate(cls, name: str, value: Any) -> None:
        """
        Partially validate audio extract options
        """
        if isinstance(value, dict):
            value["codec"] = value.get("codec", "mp3")
        _ = cls(name, value)

    def __init__(self, name, value):
        super().__init__(name, value)
        self._codec = self._validate_key(key="codec", validator=AudioTypeValidator).value
        self._quality = self._validate_key_if_present(key="quality", validator=FloatValidator)

    @property
    def codec(self) -> str:
        """
        :expected type: String
        :description:
          The codec to output after extracting the audio. Supported codecs are aac, flac, mp3, m4a,
          opus, vorbis, wav, and best to grab the best possible format at runtime.
        """
        return self._codec

    @property
    def quality(self) -> Optional[float]:
        """
        :expected type: Float
        :description:
          Optional. Specify ffmpeg audio quality. Insert a value between ``0`` (better) and ``9``
          (worse) for variable bitrate, or a specific bitrate like ``128`` for 128k.
        """
        if self._quality is not None:
            return self._quality.value
        return None

    def modified_variables(self) -> Dict[PluginOperation, Set[str]]:
        """
        Possibly changes ``ext``, so do not resolve until this has run
        """
        return {PluginOperation.MODIFY_ENTRY: {v.ext.variable_name}}


class AudioExtractPlugin(Plugin[AudioExtractOptions]):
    plugin_options_type = AudioExtractOptions

    def ytdl_options(self) -> Optional[Dict]:
        """
        Returns
        -------
        YTDL options for extracting audio
        """
        ytdl_options_builder = YTDLOptionsBuilder()

        postprocessor_dict = {
            "key": "FFmpegExtractAudio",
            "when": "post_process",
            "preferredcodec": self.plugin_options.codec,
        }
        if self.plugin_options.quality is not None:
            postprocessor_dict["preferredquality"] = self.plugin_options.quality

        return ytdl_options_builder.add(
            {
                "postprocessors": [postprocessor_dict],
                "format": "bestaudio/best",
                "keepvideo": False,
            }
        ).to_dict()

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        """
        Parameters
        ----------
        entry
            Entry with extracted audio

        Returns
        -------
        Entry with updated 'ext' source variable

        Raises
        ------
        FileNotDownloadedException
            If the audio file is not found
        """
        extracted_audio_file = entry.get_download_file_path()

        # yt-dlp doesn't record which ext is used, so try to find it
        if self.plugin_options.codec == "best":
            new_ext = "m4a"

            for possible_ext in AUDIO_CODEC_EXTS:
                extracted_audio_file = (
                    entry.get_download_file_path().removesuffix(entry.ext) + possible_ext
                )

                if os.path.isfile(extracted_audio_file):
                    new_ext = possible_ext
                    break
        else:
            new_ext = AUDIO_CODEC_TYPES_EXTENSION_MAPPING[self.plugin_options.codec]
            extracted_audio_file = entry.get_download_file_path().removesuffix(entry.ext) + new_ext

        entry.add({v.ext: new_ext})

        if not self.is_dry_run:
            if not os.path.isfile(extracted_audio_file):
                raise FileNotDownloadedException("Failed to find the extracted audio file")

        return entry

    def post_process_entry(self, entry: Entry) -> Optional[FileMetadata]:
        """
        Warn the user that best cannot infer the format that will be used at run-time.
        """
        if self.plugin_options.codec == "best" and self.is_dry_run:
            return FileMetadata(
                "Caution: extracted audio with 'best' format is not known during dry-run. "
                "Defaulting to m4a."
            )
        return None
