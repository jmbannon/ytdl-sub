from pathlib import Path
from typing import Dict
from typing import final

from ytdl_subscribe.entries.base_entry import BaseEntry
from ytdl_subscribe.entries.variables.entry_variables import EntryVariables


class Entry(EntryVariables, BaseEntry):
    """
    Entry object to represent a single media object returned from yt-dlp.
    """

    def get_download_file_path(self) -> str:
        """Returns the entry's file path to where it was downloaded"""
        return str(Path(self.working_directory()) / f"{self.uid}.{self.ext}")

    def get_download_thumbnail_path(self) -> str:
        """Returns the entry's thumbnail's file path to where it was downloaded"""
        return str(Path(self.working_directory()) / f"{self.uid}.{self.thumbnail_ext}")

    @final
    def to_dict(self) -> Dict[str, str]:
        """
        Returns
        -------
        The variables in dictionary format
        """
        return self._to_dict()
