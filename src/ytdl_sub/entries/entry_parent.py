import os
from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.entry import Entry


class EntryParent(BaseEntry):
    def __init__(self, entry_dict: Dict, working_directory: str):
        super().__init__(entry_dict=entry_dict, working_directory=working_directory)
        self.child_entries: List["EntryParent"] = []

    def parent_children(self) -> List["EntryParent"]:
        """This parent's children that are also parents"""
        return [child for child in self.child_entries if self.is_entry_parent(child)]

    def entry_children(self) -> List[Entry]:
        """This parent's children that are entries"""
        return [child.to_type(Entry) for child in self.child_entries if self.is_entry(child)]

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
                    ).read_children_from_entry_dicts(entry_dicts)
                )

        self.child_entries = sorted(child_entries, key=lambda entry: entry.kwargs("playlist_index"))
        return self

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

    def __contains__(self, item: Dict | BaseEntry) -> bool:
        playlist_id: Optional[str] = None
        if isinstance(item, dict):
            playlist_id = item.get("playlist_id")
        elif isinstance(item, BaseEntry):
            playlist_id = item.kwargs_get("playlist_id")

        if not playlist_id:
            return False

        return self.uid == playlist_id or any(
            child.__contains__(item) for child in self.child_entries
        )

    @classmethod
    def from_entry_dicts(
        cls, entry_dicts: List[Dict], working_directory: str
    ) -> List["EntryParent"]:
        """
        Reads all entry dicts and builds a tree of EntryParents
        """
        parents = [
            EntryParent(
                entry_dict=entry_dict, working_directory=working_directory
            ).read_children_from_entry_dicts(entry_dicts)
            for entry_dict in entry_dicts
            if cls.is_entry_parent(entry_dict)
        ]

        if not parents:
            return []

        # find disconnected root parent if one exists
        first_parent = min(
            parents, key=lambda x: os.stat(x.get_download_info_json_path()).st_ctime_ns
        )
        if len(first_parent.child_entries) == 0:
            parents.remove(first_parent)
            first_parent.child_entries = parents

            return [first_parent]

        return parents

    @classmethod
    def from_entry_dicts_with_no_parents(
        cls, parents: List["EntryParent"], entry_dicts: List[Dict], working_directory: str
    ) -> List[Entry]:
        """
        Reads all entries that do not have any parents
        """

        def _in_any_parents(entry_dict: Dict):
            return any(entry_dict in parent for parent in parents)

        return [
            Entry(entry_dict=entry_dict, working_directory=working_directory)
            for entry_dict in entry_dicts
            if cls.is_entry(entry_dict) and not _in_any_parents(entry_dict)
        ]
