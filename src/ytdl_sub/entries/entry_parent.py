import math
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.base_entry import TBaseEntry
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import MetadataVariable
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions
from ytdl_sub.entries.script.variable_scripts import ENTRY_DEFAULT_VARIABLES
from ytdl_sub.entries.script.variable_scripts import ENTRY_REQUIRED_VARIABLES

v: VariableDefinitions = VARIABLES


# pylint: disable=protected-access


class EntryParent(BaseEntry):
    @classmethod
    def _sort_entries(cls, entries: List[TBaseEntry]) -> List[TBaseEntry]:
        """Try sorting by playlist_id first, then fall back to uid"""
        return sorted(
            entries,
            key=lambda ent: (ent._kwargs_get(v.playlist_index.metadata_key, math.inf), ent.uid),
        )

    def __init__(self, entry_dict: Dict, working_directory: str):
        super().__init__(entry_dict=entry_dict, working_directory=working_directory)
        self._parent_children: List["EntryParent"] = []
        self._entry_children: List[Entry] = []

    def parent_children(self) -> List["EntryParent"]:
        """This parent's children that are also parents"""
        return self._parent_children

    def entry_children(self) -> List[Entry]:
        """This parent's children that are entries"""
        return self._entry_children

    def num_children(self) -> int:
        """
        Returns
        -------
        Total number of (nested) entry children
        """
        return sum(parent.num_children() for parent in self.parent_children()) + len(
            self.entry_children()
        )

    def _sibling_entry_metadata(self) -> List[Dict[str, Any]]:
        sibling_entry_metadata: List[Dict[str, Any]] = []
        variable_filter: List[MetadataVariable] = list(ENTRY_REQUIRED_VARIABLES.keys()) + list(
            ENTRY_DEFAULT_VARIABLES.keys()
        )
        for entry in self.entry_children():
            sibling_entry_metadata.append(
                {var.metadata_key: entry._kwargs_get(var.metadata_key) for var in variable_filter}
            )
        return sibling_entry_metadata

    def _set_child_variables(self, parents: Optional[List["EntryParent"]] = None) -> "EntryParent":
        if parents is None:
            parents = [self]

        kwargs_to_add: Dict[str, Any] = {
            v.sibling_metadata.metadata_key: self._sibling_entry_metadata()
        }
        if len(parents) >= 1:
            kwargs_to_add[v.playlist_metadata.metadata_key] = parents[-1]._kwargs
        if len(parents) >= 2:
            kwargs_to_add[v.source_metadata.metadata_key] = parents[-2]._kwargs
        if len(parents) >= 3:
            raise ValueError(
                "ytdl-sub currently does support more than 3 layers of playlists/entries. "
                "If you encounter this error, please file a ticket with the URLs used."
            )

        for entry_child in self.entry_children():
            entry_child._kwargs = dict(entry_child._kwargs, **kwargs_to_add)

        for parent_child in self.parent_children():
            parent_child._set_child_variables(parents=parents + [parent_child])

        return self

    def _read_children_from_entry_dicts(self, entry_dicts: List[Dict]) -> "EntryParent":
        """
        Populates a tree of EntryParents that belong to this instance
        """
        entries = [
            EntryParent(
                entry_dict=entry_dict,
                working_directory=self.working_directory(),
            )._read_children_from_entry_dicts(entry_dicts)
            for entry_dict in entry_dicts
            if entry_dict in self
        ]

        self._parent_children = self._sort_entries(
            [ent for ent in entries if self.is_entry_parent(ent)]
        )
        self._entry_children = self._sort_entries(
            [ent.to_type(Entry) for ent in entries if self.is_entry(ent)]
        )

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
        for thumbnail in self._kwargs_get("thumbnails", []):
            if thumbnail["id"] == thumbnail_id:
                return thumbnail["url"]
        return None

    def __contains__(self, item: Dict | BaseEntry) -> bool:
        playlist_id: Optional[str] = None
        if isinstance(item, dict):
            playlist_id = item.get("playlist_id")
        elif isinstance(item, BaseEntry):
            playlist_id = item._kwargs_get("playlist_id")

        if not playlist_id:
            return False

        return self.uid == playlist_id or any(item in child for child in self.parent_children())

    @classmethod
    def _get_disconnected_root_parent(
        cls, url: str, parents: List["EntryParent"]
    ) -> Optional["EntryParent"]:
        """
        Sometimes the root-level parent is disconnected via playlist_ids Find it if it exists.
        """

        def _url_matches(parent: "EntryParent"):
            return parent.webpage_url in url or url in parent.webpage_url

        def _uid_is_uploader_id(parent: "EntryParent"):
            return parent.uid == parent.uploader_id

        top_level_parents = [
            parent for parent in parents if parent.num_children() == 0 and _url_matches(parent)
        ]

        # If more than 1 parent exists, assume the uploader_id is the root parent
        if len(top_level_parents) > 1:
            top_level_parents = [parent for parent in parents if _uid_is_uploader_id(parent)]

        match len(top_level_parents):
            case 0:
                return None
            case 1:
                return top_level_parents[0]
            case 2:
                # Channels can have two of the same .info.json. Handle it here
                top0 = top_level_parents[0]
                top1 = top_level_parents[1]
                if top0.uploader_id == top1.uploader_id:
                    return top0 if not top0.webpage_url.endswith("/videos") else top1

        raise ValueError(
            "Detected multiple top-level parents. "
            "Please file an issue on GitHub with the URLs used to produce this error"
        )

    @classmethod
    def from_entry_dicts(
        cls, url: str, entry_dicts: List[Dict], working_directory: str
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

        # If a disconnected root parent exists, connect it here
        if (root_parent := cls._get_disconnected_root_parent(url, parents)) is not None:
            parents.remove(root_parent)
            root_parent._parent_children = parents
            parents = [root_parent]

        for parent in parents:
            parent._set_child_variables()

        return parents

    @classmethod
    def from_entry_dicts_with_no_parents(
        cls,
        parents: List["EntryParent"],
        entry_dicts: List[Dict],
        working_directory: str,
    ) -> List[Entry]:
        """
        Reads all entries that do not have any parents
        """

        def _in_any_parents(entry_dict: Dict):
            return any(entry_dict in parent for parent in parents)

        return [
            Entry(
                entry_dict=entry_dict,
                working_directory=working_directory,
            )
            for entry_dict in entry_dicts
            if cls.is_entry(entry_dict) and not _in_any_parents(entry_dict)
        ]
