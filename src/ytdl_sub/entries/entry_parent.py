from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from ytdl_sub.entries.base_entry import BaseEntry

TBaseEntry = TypeVar("TBaseEntry", bound=BaseEntry)


class EntryParent(BaseEntry):
    def __init__(self, entry_dict: Dict, working_directory: str):
        super().__init__(entry_dict=entry_dict, working_directory=working_directory)
        self.child_entries: List["EntryParent"] = []

    def is_entry(self) -> bool:
        """
        Returns
        -------
        True if the entry contains a media file. False otherwise.
        """
        return self.kwargs_contains("ext")

    def parent_children(self) -> List["EntryParent"]:
        """This parent's children that are also parents"""
        return [child for child in self.child_entries if child.child_count() > 0]

    def entry_children(self) -> List["EntryParent"]:
        """This parent's children that are entries"""
        return [child for child in self.child_entries if child.is_entry()]

    def read_children_from_entry_dicts(self, entry_dicts: List[Dict]) -> "EntryParent":
        """
        Populates a tree of EntryParents that belong to this instance
        """
        child_entries: List["EntryParent"] = []

        for entry_dict in entry_dicts:
            if entry_dict.get("playlist_id") == self.uid:
                child_entries.append(
                    self.__class__(
                        entry_dict=entry_dict,
                        working_directory=self.working_directory(),
                    )
                )
                child_entries[-1].read_children_from_entry_dicts(entry_dicts)

        self.child_entries = sorted(child_entries, key=lambda entry: entry.kwargs("playlist_index"))
        return self

    def child_count(self) -> int:
        """
        Returns
        -------
        Number of child entries
        """
        return len(self.child_entries)

    def get_thumbnail_url(self, thumbnail_id: str) -> Optional[str]:
        """
        Downloads a specific thumbnail from a YTDL entry's thumbnail list

        Parameters
        ----------
        thumbnail_id:
            Id of the thumbnail defined in the parent's thumbnail

        Returns
        -------
        Desired thumbnail url if it exists. None if it does not.
        """
        for thumbnail in self.kwargs_get("thumbnails", []):
            if thumbnail["id"] == thumbnail_id:
                return thumbnail["url"]
        return None

    @classmethod
    def from_entry_dicts(
        cls, entry_dicts: List[Dict], working_directory: str
    ) -> List["EntryParent"]:
        """
        Reads all entry dicts and builds a tree of EntryParents
        """
        return [
            EntryParent(
                entry_dict=entry_dict, working_directory=working_directory
            ).read_children_from_entry_dicts(entry_dicts)
            for entry_dict in entry_dicts
            if "playlist_id" not in entry_dict
        ]

    def to_type(self, entry_type: Type[TBaseEntry]) -> TBaseEntry:
        """
        Returns
        -------
        Converted EntryParent to Entry-like class
        """
        return entry_type(entry_dict=self._kwargs, working_directory=self._working_directory)
