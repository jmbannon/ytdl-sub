import os.path
from typing import Dict
from typing import Optional

from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.plugins.plugin import Plugin
from ytdl_sub.plugins.plugin import PluginOptions
from ytdl_sub.utils.exceptions import FileNotDownloadedException
from ytdl_sub.validators.string_select_validator import StringSelectValidator
from ytdl_sub.validators.validators import FloatValidator

CODEC_TYPES_EXTENSION_MAPPING: Dict[str, str] = {
    "aac": "aac",
    "flac": "flac",
    "mp3": "mp3",
    "m4a": "m4a",
    "opus": "opus",
    "vorbis": "ogg",
    "wav": "wav",
}


class CodecTypeValidator(StringSelectValidator):
    _expected_value_type_name = "codec"
    _select_values = set(CODEC_TYPES_EXTENSION_MAPPING.keys())


class AudioExtractOptions(PluginOptions):
    """
    Extracts audio from a video file

    Usage:

    .. code-block:: yaml

       presets:
         my_example_preset:
           audio_extract:
             codec: "mp3"
             quality: 128
    """

    _optional_keys = {"codec", "quality"}

    def __init__(self, name, value):
        super().__init__(name, value)
        self._codec = self._validate_key(key="codec", validator=CodecTypeValidator).value
        self._quality = self._validate_key_if_present(key="quality", validator=FloatValidator)

    @property
    def codec(self) -> str:
        """
        The codec to output after extracting the audio. Supported codecs are aac, flac, mp3, m4a,
        opus, vorbis, wav.
        """
        return self._codec

    @property
    def quality(self) -> Optional[float]:
        """
        Optional. Specify ffmpeg audio quality. Insert a value between ``0`` (better) and ``9``
        (worse) for VBR or a specific bitrate like ``128`` for 128k.
        """
        if self._quality is not None:
            return self._quality.value
        return None


class AudioExtractPlugin(Plugin[AudioExtractOptions]):
    plugin_options_type = AudioExtractOptions

    def ytdl_options(self) -> Optional[Dict]:
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
            }
        ).to_dict()

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        new_ext = CODEC_TYPES_EXTENSION_MAPPING[self.plugin_options.codec]
        extracted_audio_file = entry.get_download_file_path().removesuffix(entry.ext) + new_ext
        if not self.is_dry_run:
            if not os.path.isfile(extracted_audio_file):
                raise FileNotDownloadedException("Failed to find the extracted audio file")

        entry._kwargs["ext"] = new_ext
        return entry
