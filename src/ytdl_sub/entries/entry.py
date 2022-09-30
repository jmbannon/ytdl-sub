import copy
import json
import os
from pathlib import Path
from typing import Optional
from typing import final

from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.variables.entry_variables import EntryVariables
from ytdl_sub.validators.audo_codec_validator import AUDIO_CODEC_EXTS


class Entry(EntryVariables, BaseEntry):
    """
    Entry object to represent a single media object returned from yt-dlp.
    """

    @property
    def ext(self) -> str:
        """
        With ffmpeg installed, yt-dlp will sometimes merge the file into an mkv file.
        This is not reflected in the entry. See if the mkv file exists and return "mkv" if so,
        otherwise, return the original extension.
        """
        mkv_file_path = str(Path(self.working_directory()) / f"{self.uid}.mkv")
        if os.path.isfile(mkv_file_path):
            return "mkv"
        return super().ext

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
        return f"{self.uid}.{self.thumbnail_ext}"

    def get_download_thumbnail_path(self) -> str:
        """Returns the entry's thumbnail's file path to where it was downloaded"""
        return str(Path(self.working_directory()) / self.get_download_thumbnail_name())

    def get_ytdlp_download_thumbnail_path(self) -> Optional[str]:
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
    def is_downloaded(self) -> bool:
        """
        Returns
        -------
        True if the file and thumbnail exist locally. False otherwise.
        """
        file_exists = os.path.isfile(self.get_download_file_path())

        # HACK: yt-dlp does not record extracted audio extensions anywhere. If the file is not
        # found, try it using audio extensions
        if not file_exists:
            for audio_ext in AUDIO_CODEC_EXTS:
                if os.path.isfile(self.get_download_file_path().removesuffix(self.ext) + audio_ext):
                    file_exists = True
                    break

        return file_exists
