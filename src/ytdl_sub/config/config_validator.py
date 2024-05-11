import os
import posixpath
from typing import Any
from typing import Dict
from typing import Optional

from mergedeep import mergedeep
from yt_dlp.utils import datetime_from_str

from ytdl_sub.config.defaults import DEFAULT_FFMPEG_PATH
from ytdl_sub.config.defaults import DEFAULT_FFPROBE_PATH
from ytdl_sub.config.defaults import DEFAULT_LOCK_DIRECTORY
from ytdl_sub.config.defaults import MAX_FILE_NAME_BYTES
from ytdl_sub.prebuilt_presets import PREBUILT_PRESETS
from ytdl_sub.validators.file_path_validators import FFmpegFileValidator
from ytdl_sub.validators.file_path_validators import FFprobeFileValidator
from ytdl_sub.validators.strict_dict_validator import StrictDictValidator
from ytdl_sub.validators.validators import BoolValidator
from ytdl_sub.validators.validators import IntValidator
from ytdl_sub.validators.validators import LiteralDictValidator
from ytdl_sub.validators.validators import StringValidator


class ExperimentalValidator(StrictDictValidator):
    _optional_keys = {"enable_update_with_info_json"}
    _allow_extra_keys = True

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        self._enable_update_with_info_json = self._validate_key(
            key="enable_update_with_info_json", validator=BoolValidator, default=False
        )

    @property
    def enable_update_with_info_json(self) -> bool:
        """
        Enables modifying subscription files using info.json files using the argument
        ``--update-with-info-json``. This feature is still being tested and has the ability to
        destroy files. Ensure you have a full backup before usage. You have been warned!
        """
        return self._enable_update_with_info_json.value


class PersistLogsValidator(StrictDictValidator):
    _required_keys = {"logs_directory"}
    _optional_keys = {"keep_logs_after", "keep_successful_logs"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        self._logs_directory = self._validate_key(key="logs_directory", validator=StringValidator)

        self._keep_logs_after: Optional[str] = None
        if keep_logs_validator := self._validate_key_if_present(
            key="keep_logs_after", validator=StringValidator
        ):
            try:
                self._keep_logs_after = datetime_from_str(keep_logs_validator.value)
            except Exception as exc:
                raise self._validation_exception(f"Invalid datetime string: {str(exc)}")

        self._keep_successful_logs = self._validate_key(
            key="keep_successful_logs", validator=BoolValidator, default=True
        )

    @property
    def logs_directory(self) -> str:
        """
        Required. The directory to store the logs in.
        """
        return self._logs_directory.value

    # pylint: disable=line-too-long
    # @property
    # def keep_logs_after(self) -> Optional[str]:
    #     """
    #     Optional. Keep logs after this date, in yt-dlp datetime format.
    #
    #     .. code-block:: Markdown
    #
    #        A string in the format YYYYMMDD or
    #        (now|today|yesterday|date)[+-][0-9](microsecond|second|minute|hour|day|week|month|year)(s)
    #
    #     For example, ``today-1week`` means keep 1 week's worth of logs. By default, ytdl-sub will
    #     keep all log files.
    #     """
    #     return self._keep_logs_after

    # pylint: enable=line-too-long

    @property
    def keep_successful_logs(self) -> bool:
        """
        Optional. Whether to store logs when downloading is successful. Defaults to True.
        """
        return self._keep_successful_logs.value


class ConfigOptions(StrictDictValidator):
    _optional_keys = {
        "working_directory",
        "umask",
        "dl_aliases",
        "persist_logs",
        "lock_directory",
        "ffmpeg_path",
        "ffprobe_path",
        "file_name_max_bytes",
        "experimental",
    }

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)

        self._working_directory = self._validate_key_if_present(
            key="working_directory",
            validator=StringValidator,
            default=".ytdl-sub-working-directory",
        )
        self._umask = self._validate_key_if_present(
            key="umask", validator=StringValidator, default="022"
        )
        self._dl_aliases = self._validate_key_if_present(
            key="dl_aliases", validator=LiteralDictValidator
        )
        self._persist_logs = self._validate_key_if_present(
            key="persist_logs", validator=PersistLogsValidator
        )
        self._lock_directory = self._validate_key(
            key="lock_directory", validator=StringValidator, default=DEFAULT_LOCK_DIRECTORY
        )
        self._ffmpeg_path = self._validate_key(
            key="ffmpeg_path", validator=FFmpegFileValidator, default=DEFAULT_FFMPEG_PATH
        )
        self._ffprobe_path = self._validate_key(
            key="ffprobe_path", validator=FFprobeFileValidator, default=DEFAULT_FFPROBE_PATH
        )
        self._experimental = self._validate_key(
            key="experimental", validator=ExperimentalValidator, default={}
        )
        self._file_name_max_bytes = self._validate_key(
            key="file_name_max_bytes", validator=IntValidator, default=MAX_FILE_NAME_BYTES
        )

    @property
    def working_directory(self) -> str:
        """
        The directory to temporarily store downloaded files before moving them into their final
        directory. Defaults to .ytdl-sub-working-directory
        """
        # Expands tildas to actual paths, use native os sep
        return os.path.expanduser(self._working_directory.value.replace(posixpath.sep, os.sep))

    @property
    def umask(self) -> Optional[str]:
        """
        Umask (octal format) to apply to every created file. Defaults to "022".
        """
        return self._umask.value

    @property
    def dl_aliases(self) -> Optional[Dict[str, str]]:
        """
        .. _dl_aliases:

        Alias definitions to shorten ``ytdl-sub dl`` arguments. For example,

        .. code-block:: yaml

           configuration:
             dl_aliases:
               mv: "--preset music_video"
               u: "--download.url"

        Simplifies

        .. code-block:: bash

           ytdl-sub dl --preset "Jellyfin Music Videos" --download.url "youtube.com/watch?v=a1b2c3"

        to

        .. code-block:: bash

           ytdl-sub dl --mv --u "youtube.com/watch?v=a1b2c3"
        """
        if self._dl_aliases:
            return self._dl_aliases.dict
        return {}

    @property
    def persist_logs(self) -> Optional[PersistLogsValidator]:
        """
        Persist logs validator. readthedocs in the validator itself!
        """
        return self._persist_logs

    @property
    def file_name_max_bytes(self) -> int:
        """
        Max file name size in bytes. Most OS's typically default to 255 bytes.
        """
        return self._file_name_max_bytes.value

    @property
    def experimental(self) -> ExperimentalValidator:
        """
        Experimental validator. readthedocs in the validator itself!
        """
        return self._experimental

    @property
    def lock_directory(self) -> str:
        """
        The directory to temporarily store file locks, which prevents multiple instances
        of ``ytdl-sub`` from running. Note that file locks do not work on network-mounted
        directories. Ensure that this directory resides on the host machine. Defaults to ``/tmp``.
        """
        return self._lock_directory.value

    @property
    def ffmpeg_path(self) -> str:
        """
        Path to ffmpeg executable. Defaults to ``/usr/bin/ffmpeg`` for Linux, and
        ``ffmpeg.exe`` for Windows (in the same directory as ytdl-sub).
        """
        return self._ffmpeg_path.value

    @property
    def ffprobe_path(self) -> str:
        """
        Path to ffprobe executable. Defaults to ``/usr/bin/ffprobe`` for Linux, and
        ``ffprobe.exe`` for Windows (in the same directory as ytdl-sub).
        """
        return self._ffprobe_path.value


class ConfigValidator(StrictDictValidator):
    _optional_keys = {"configuration", "presets"}

    def __init__(self, name: str, value: Any):
        super().__init__(name, value)
        self.config_options = self._validate_key_if_present(
            "configuration", ConfigOptions, default={}
        )

        # Make sure presets is a dictionary. Will be validated in `PresetValidator`
        self.presets = self._validate_key_if_present("presets", LiteralDictValidator, default={})

        # Ensure custom presets do not collide with prebuilt presets
        for preset_name in self.presets.keys:
            if preset_name in PREBUILT_PRESETS:
                raise self._validation_exception(
                    f"preset name '{preset_name}' conflicts with a prebuilt preset"
                )

        # Merge prebuilt presets into the config so custom presets can use them
        mergedeep.merge(self.presets._value, PREBUILT_PRESETS)
