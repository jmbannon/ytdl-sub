# pylint: disable=protected-access
import copy
import json
import os
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Optional
from typing import Type
from typing import TypeVar
from typing import final

from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions
from ytdl_sub.entries.script.variable_types import ArrayVariable
from ytdl_sub.entries.script.variable_types import StringVariable
from ytdl_sub.entries.script.variable_types import Variable
from ytdl_sub.script.utils.exceptions import ScriptVariableNotResolved
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.utils.scriptable import Scriptable
from ytdl_sub.validators.audo_codec_validator import AUDIO_CODEC_EXTS
from ytdl_sub.validators.audo_codec_validator import VIDEO_CODEC_EXTS

v: VariableDefinitions = VARIABLES

_YTDL_SUB_ENTRY_VARIABLES_KWARG_KEY: str = "ytdl_sub_entry_variables"
ytdl_sub_chapters_from_comments = ArrayVariable(
    "ytdl_sub_chapters_from_comments", definition="{ [] }"
)
ytdl_sub_split_by_chapters_parent_uid = StringVariable(
    "ytdl_sub_split_by_chapters_parent_uid", definition="{ %string('') }"
)

TypeT = TypeVar("TypeT")


class Entry(BaseEntry, Scriptable):
    """
    Entry object to represent a single media object returned from yt-dlp.
    """

    def __init__(self, entry_dict: Dict, working_directory: str):
        BaseEntry.__init__(self, entry_dict=entry_dict, working_directory=working_directory)
        Scriptable.__init__(self)

    def initialize_script(self, other: Optional[Scriptable] = None) -> "Entry":
        """
        Initializes the entry script using the Overrides script, then adding
        its kwargs to the entry metadata variable
        """
        # Overrides contains added variables that are unresolvable, add them here
        if other:
            self._script = copy.deepcopy(other.script)
            self._unresolvable = copy.deepcopy(other.unresolvable)
        else:
            self.initialize_base_script()

        self._add_entry_kwargs_to_script()
        return self

    def _add_entry_kwargs_to_script(self) -> None:
        # Add entry metadata, but avoid the `.add()` helper since it also adds sanitized
        self.unresolvable.remove(v.entry_metadata.variable_name)
        self.script.add({v.entry_metadata.variable_name: ScriptUtils.to_script(self._kwargs)})
        self.update_script()

    def get(self, variable: Variable, expected_type: Type[TypeT]) -> TypeT:
        """
        Gets a variable of an expected type. Will error if it does not exist or is not resolved.
        """
        out = self.script.resolve(unresolvable=self.unresolvable).get_native(variable.variable_name)
        return expected_type(out)

    def try_get(self, variable: Variable, expected_type: Type[TypeT]) -> Optional[TypeT]:
        """
        Gets a variable of an expected type. Returns None if it does not exist or is not resolved.
        """
        try:
            return self.get(variable=variable, expected_type=expected_type)
        except ScriptVariableNotResolved:
            return None

    def add_injected_variables(
        self, download_entry: "Entry", download_idx: int, upload_date_idx: int
    ) -> "Entry":
        """
        Adds variables that get injected into the Entry script that aren't available at
        metadata scrape time (only after the actual download).
        """
        self.add(
            {
                # Tracks number of entries downloaded
                v.download_index: download_idx + 1,
                # Tracks number of entries with the same upload date to make them unique
                v.upload_date_index: upload_date_idx + 1,
                v.requested_subtitles: download_entry._kwargs_get(
                    v.requested_subtitles.metadata_key, []
                ),
                v.chapters: download_entry._kwargs_get(v.chapters.metadata_key, []),
                v.sponsorblock_chapters: download_entry._kwargs_get(
                    v.sponsorblock_chapters.metadata_key, []
                ),
                v.comments: download_entry._kwargs_get(v.comments.metadata_key, []),
            }
        )
        return self

    @property
    def ext(self) -> str:
        """
        With ffmpeg installed, yt-dlp will sometimes merge the file into an mkv file.
        This is not reflected in the entry. See if the mkv file exists and return "mkv" if so,
        otherwise, return the original extension.
        """
        ext = self.try_get(v.ext, str) or self._kwargs[v.ext.metadata_key]
        for possible_ext in [ext, "mkv"]:
            file_name = self.base_filename(ext=possible_ext)
            file_path = str(Path(self.working_directory()) / file_name)
            if os.path.isfile(file_path):
                return possible_ext

        return ext

    def get_download_file_name(self) -> str:
        """
        Returns
        -------
        The entry's file name
        """
        return self.base_filename(ext=self.ext)

    def get_download_file_path(self) -> str:
        """Returns the entry's file path to where it was downloaded"""
        return str(Path(self.working_directory()) / self.get_download_file_name())

    def get_download_thumbnail_name(self) -> str:
        """
        Returns
        -------
        The download thumbnail's file name
        """
        return self.base_filename(ext=self.get(v.thumbnail_ext, str))

    def get_download_thumbnail_path(self) -> str:
        """Returns the entry's thumbnail's file path to where it was downloaded"""
        return str(Path(self.working_directory()) / self.get_download_thumbnail_name())

    def try_get_ytdlp_download_thumbnail_path(self) -> Optional[str]:
        """
        The source `thumbnail` value and the actual downloaded thumbnail extension sometimes do
        not match. Return the actual downloaded thumbnail path.
        """
        thumbnails = self._kwargs_get("thumbnails", [])
        possible_thumbnail_exts = {"jpg", "webp"}  # Always check for jpg and webp thumbs

        for thumbnail in thumbnails:
            possible_thumbnail_exts.add(thumbnail["url"].split(".")[-1])

        for ext in possible_thumbnail_exts:
            possible_thumbnail_filename = self.base_filename(ext=ext)
            possible_thumbnail_path = str(
                Path(self.working_directory()) / possible_thumbnail_filename
            )
            if os.path.isfile(possible_thumbnail_path):
                return possible_thumbnail_path

        return None

    def write_info_json(self) -> None:
        """
        Write the entry's _kwargs back into the info.json file as well as its source variables
        """
        kwargs_dict = copy.deepcopy(self._kwargs)
        kwargs_dict[_YTDL_SUB_ENTRY_VARIABLES_KWARG_KEY] = self.to_dict()
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
            for ext in AUDIO_CODEC_EXTS | VIDEO_CODEC_EXTS:
                if os.path.isfile(self.get_download_file_path().removesuffix(self.ext) + ext):
                    file_exists = True
                    break

        return file_exists

    def maybe_get_prior_variables(self) -> Dict[str, Any]:
        """
        If variables exist in the .info.json from a prior run, delete them
        from kwargs (to prevent nested writes) and return them
        """
        maybe_prior_variables: Dict[str, Any] = {}
        if _YTDL_SUB_ENTRY_VARIABLES_KWARG_KEY in self._kwargs:
            maybe_prior_variables = self._kwargs[_YTDL_SUB_ENTRY_VARIABLES_KWARG_KEY]
            del self._kwargs[_YTDL_SUB_ENTRY_VARIABLES_KWARG_KEY]

        return maybe_prior_variables

    @final
    def to_dict(self) -> Dict[str, Any]:
        """
        Returns
        -------
        Dictionary containing all variables
        """
        return self.script.resolve().as_native()

    @classmethod
    def create_split_entry(cls, entry: "Entry", new_uid: str) -> "Entry":
        """
        Creates a copy of an entry with a new uid to use as the starting point for a split entry
        """
        new_entry = copy.deepcopy(entry)
        new_entry._kwargs[v.uid.metadata_key] = new_uid
        new_entry.add(
            {
                v.uid.variable_name: new_uid,
                ytdl_sub_split_by_chapters_parent_uid.variable_name: entry.uid,
            }
        )
        return new_entry
