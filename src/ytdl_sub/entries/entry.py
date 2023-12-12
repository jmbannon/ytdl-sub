import copy
import json
import os
from pathlib import Path
from typing import Dict
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import final

from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.script.variable_definitions import VARIABLES as v
from ytdl_sub.entries.script.variable_definitions import Variable
from ytdl_sub.script.utils.exceptions import ScriptVariableNotResolved
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.utils.scriptable import Scriptable
from ytdl_sub.validators.audo_codec_validator import AUDIO_CODEC_EXTS
from ytdl_sub.validators.audo_codec_validator import VIDEO_CODEC_EXTS

YTDL_SUB_ENTRY_VARIABLES_KWARG_KEY: str = "ytdl_sub_entry_variables"

TType = TypeVar("TType")


class Entry(BaseEntry, Scriptable):
    """
    Entry object to represent a single media object returned from yt-dlp.
    """

    def __init__(self, entry_dict: Dict, working_directory: str):
        BaseEntry.__init__(self, entry_dict=entry_dict, working_directory=working_directory)
        Scriptable.__init__(self)

    def _add_entry_kwargs_to_script(self) -> None:
        # Add entry metadata, but avoid the `.add()` helper since it also adds sanitized
        self.unresolvable.remove(v.entry_metadata.variable_name)
        self.script.add({v.entry_metadata.variable_name: ScriptUtils.to_script(self._kwargs)})
        self.update_script()

    def initialize_script(self, other: Optional[Scriptable] = None) -> "Entry":
        # TODO: CLEAN THIS SHIT UP
        # Overrides contains added variables that are unresolvable, add them here
        if other:
            self.script = copy.deepcopy(other.script)
            self.unresolvable = copy.deepcopy(other.unresolvable)

        self._add_entry_kwargs_to_script()
        return self

    def get(self, variable: Variable, expected_type: Type[TType]) -> TType:
        out = self.script.resolve(unresolvable=self.unresolvable).get_native(variable.variable_name)
        return expected_type(out)

    def try_get(self, variable: Variable, expected_type: Type[TType]) -> Optional[TType]:
        try:
            return self.get(variable=variable, expected_type=expected_type)
        except ScriptVariableNotResolved:
            return None

    def get_str(self, variable: Variable) -> str:
        return self.get(variable, str)

    def get_int(self, variable: Variable) -> int:
        return self.get(variable, int)

    @property
    def ext(self) -> str:
        """
        With ffmpeg installed, yt-dlp will sometimes merge the file into an mkv file.
        This is not reflected in the entry. See if the mkv file exists and return "mkv" if so,
        otherwise, return the original extension.
        """
        ext = self.try_get(v.ext, str) or self.kwargs(key=v.ext.metadata_key)
        for possible_ext in [ext, "mkv"]:
            file_path = str(Path(self.working_directory()) / f"{self.uid}.{possible_ext}")
            if os.path.isfile(file_path):
                return possible_ext

        return ext

    def get_download_file_name(self) -> str:
        """
        Returns
        -------
        The entry's file name
        """
        return f"{self.uid}.{self.ext}"

    def get_download_file_path(self) -> str:
        """Returns the entry's file path to where it was downloaded"""
        return str(Path(self.working_directory()) / self.get_download_file_name())

    def get_download_thumbnail_name(self) -> str:
        """
        Returns
        -------
        The download thumbnail's file name
        """
        return f"{self.get_str(v.uid)}.{self.get_str(v.thumbnail_ext)}"

    def get_download_thumbnail_path(self) -> str:
        """Returns the entry's thumbnail's file path to where it was downloaded"""
        return str(Path(self.working_directory()) / self.get_download_thumbnail_name())

    def try_get_ytdlp_download_thumbnail_path(self) -> Optional[str]:
        """
        The source `thumbnail` value and the actual downloaded thumbnail extension sometimes do
        not match. Return the actual downloaded thumbnail path.
        """
        thumbnails = self.kwargs_get("thumbnails", [])
        possible_thumbnail_exts = {"jpg", "webp"}  # Always check for jpg and webp thumbs

        for thumbnail in thumbnails:
            possible_thumbnail_exts.add(thumbnail["url"].split(".")[-1])

        for ext in possible_thumbnail_exts:
            possible_thumbnail_path = str(Path(self.working_directory()) / f"{self.uid}.{ext}")
            if os.path.isfile(possible_thumbnail_path):
                return possible_thumbnail_path

        return None

    def write_info_json(self) -> None:
        """
        Write the entry's _kwargs back into the info.json file as well as its source variables
        """
        kwargs_dict = copy.deepcopy(self._kwargs)
        kwargs_dict["ytdl_sub_entry_variables"] = self.to_dict()
        kwargs_json = json.dumps(kwargs_dict, ensure_ascii=False, sort_keys=True, indent=2)

        with open(self.get_download_info_json_path(), "w", encoding="utf-8") as file:
            file.write(kwargs_json)

    @final
    def is_thumbnail_downloaded_via_ytdlp(self) -> bool:
        """
        Returns
        -------
        True if ANY thumbnail file exist locally. False otherwise.
        """
        return self.try_get_ytdlp_download_thumbnail_path() is not None

    @final
    def is_thumbnail_downloaded(self) -> bool:
        """
        Returns
        -------
        True if the thumbnail file exists and is its proper format. False otherwise.
        """
        return os.path.isfile(self.get_download_thumbnail_path())

    @final
    def is_downloaded(self) -> bool:
        """
        Returns
        -------
        True if the file exist locally. False otherwise.
        """
        file_exists = os.path.isfile(self.get_download_file_path())

        # HACK: yt-dlp does not record extracted/converted extensions anywhere. If the file is not
        # found, try it using all possible extensions
        if not file_exists:
            for ext in AUDIO_CODEC_EXTS.union(VIDEO_CODEC_EXTS):
                if os.path.isfile(self.get_download_file_path().removesuffix(self.ext) + ext):
                    file_exists = True
                    break

        return file_exists

    @final
    def to_dict(self) -> Dict[str, str]:
        """
        Returns
        -------
        Dictionary containing all variables
        """
        return self.script.resolve().as_native()
