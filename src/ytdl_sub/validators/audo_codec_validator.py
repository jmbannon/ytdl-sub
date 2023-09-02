from typing import Dict
from typing import Set

from ytdl_sub.validators.string_select_validator import StringSelectValidator

AUDIO_CODEC_TYPES_EXTENSION_MAPPING: Dict[str, str] = {
    "aac": "aac",
    "flac": "flac",
    "mp3": "mp3",
    "m4a": "m4a",
    "opus": "opus",
    "vorbis": "ogg",
    "wav": "wav",
}

AUDIO_CODEC_TYPES: Set[str] = set(AUDIO_CODEC_TYPES_EXTENSION_MAPPING.keys())
AUDIO_CODEC_EXTS: Set[str] = set(AUDIO_CODEC_TYPES_EXTENSION_MAPPING.values())

VIDEO_CODEC_EXTS: Set[str] = {"avi", "flv", "mkv", "mov", "mp4", "webm"}


class AudioTypeValidator(StringSelectValidator):
    _expected_value_type_name = "codec"
    _select_values = AUDIO_CODEC_TYPES.union({"best"})  # support 'best' in the audio extract plugin


class FileTypeValidator(StringSelectValidator):
    _expected_value_type_name = "codec"
    _select_values = AUDIO_CODEC_TYPES.union(VIDEO_CODEC_EXTS)
