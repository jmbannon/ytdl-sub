import math
import os
from typing import Dict
from typing import List
from typing import Optional

import mergedeep

from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.base_entry import TBaseEntry
from ytdl_sub.entries.entry import Entry


class ParentType:
    PLAYLIST = "playlist"
    SOURCE = "source"


def _sort_entries(entries: List[TBaseEntry]) -> List[TBaseEntry]:
    """Try sorting by playlist_id first, then fall back to uid"""
    return sorted(entries, key=lambda ent: (ent.kwargs_get("playlist_id", math.inf), ent.uid))


class EntryParent(BaseEntry):
    def __init__(self, entry_dict: Dict, working_directory: str):
        super().__init__(entry_dict=entry_dict, working_directory=working_directory)
        self.child_entries: List["EntryParent"] = []

    def parent_children(self) -> List["EntryParent"]:
        """This parent's children that are also parents"""
        return _sort_entries([child for child in self.child_entries if self.is_entry_parent(child)])

    def entry_children(self) -> List[Entry]:
        """This parent's children that are entries"""
        return _sort_entries(
            [child.to_type(Entry) for child in self.child_entries if self.is_entry(child)]
        )

    def _parent_variables(self, parent_type: str) -> Dict:
        return dict(
            {f"{parent_type}_entry": self._kwargs},
            **{f"{parent_type}_{key}": value for key, value in self.base_variable_dict().items()},
        )

    # pylint: disable=protected-access

    def _set_child_variables(self, parents: Optional[List["EntryParent"]] = None) -> "EntryParent":
        if parents is None:
            parents = [self]

        kwargs_to_add: Dict = {}
        if len(parents) >= 1:
            mergedeep.merge(kwargs_to_add, parents[-1]._parent_variables(ParentType.PLAYLIST))
        if len(parents) >= 2:
            mergedeep.merge(kwargs_to_add, parents[-2]._parent_variables(ParentType.SOURCE))
        if len(parents) >= 3:
            raise ValueError(
                "ytdl-sub currently does support more than 3 layers of playlists/entries. "
                "If you encounter this error, please file a ticket with the URLs used."
            )

        for entry_child in self.entry_children():
            entry_child.add_kwargs(kwargs_to_add)

        for parent_child in self.parent_children():
            parent_child._set_child_variables(parents=parents + [parent_child])

        return self

    def _read_children_from_entry_dicts(self, entry_dicts: List[Dict]) -> "EntryParent":
        """
        Populates a tree of EntryParents that belong to this instance
        """
        child_entries = [
            EntryParent(
                entry_dict=entry_dict,
                working_directory=self.working_directory(),
            )._read_children_from_entry_dicts(entry_dicts)
            for entry_dict in entry_dicts
            if entry_dict in self
        ]

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
            )._read_children_from_entry_dicts(entry_dicts)
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

            parents = [first_parent]

        for parent in parents:
            parent._set_child_variables()

        return parents

    # pylint: enable=protected-access

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
