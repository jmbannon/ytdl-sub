import functools
import math
from typing import Dict
from typing import List
from typing import Optional

import mergedeep

from ytdl_sub.entries.base_entry import BaseEntry
from ytdl_sub.entries.base_entry import TBaseEntry
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.variables.kwargs import PLAYLIST_COUNT
from ytdl_sub.entries.variables.kwargs import PLAYLIST_DESCRIPTION
from ytdl_sub.entries.variables.kwargs import PLAYLIST_ENTRY
from ytdl_sub.entries.variables.kwargs import PLAYLIST_INDEX
from ytdl_sub.entries.variables.kwargs import PLAYLIST_MAX_UPLOAD_YEAR
from ytdl_sub.entries.variables.kwargs import PLAYLIST_MAX_UPLOAD_YEAR_TRUNCATED
from ytdl_sub.entries.variables.kwargs import PLAYLIST_TITLE
from ytdl_sub.entries.variables.kwargs import PLAYLIST_UID
from ytdl_sub.entries.variables.kwargs import PLAYLIST_WEBPAGE_URL
from ytdl_sub.entries.variables.kwargs import SOURCE_COUNT
from ytdl_sub.entries.variables.kwargs import SOURCE_DESCRIPTION
from ytdl_sub.entries.variables.kwargs import SOURCE_ENTRY
from ytdl_sub.entries.variables.kwargs import SOURCE_INDEX
from ytdl_sub.entries.variables.kwargs import SOURCE_TITLE
from ytdl_sub.entries.variables.kwargs import SOURCE_UID
from ytdl_sub.entries.variables.kwargs import SOURCE_WEBPAGE_URL


class ParentType:
    PLAYLIST = "playlist"
    SOURCE = "source"


def _sort_entries(entries: List[TBaseEntry]) -> List[TBaseEntry]:
    """Try sorting by playlist_id first, then fall back to uid"""
    return sorted(entries, key=lambda ent: (ent.kwargs_get(PLAYLIST_INDEX, math.inf), ent.uid))


class EntryParent(BaseEntry):
    def __init__(self, entry_dict: Dict, working_directory: str):
        super().__init__(entry_dict=entry_dict, working_directory=working_directory)
        self.child_entries: List["EntryParent"] = []

    @functools.cache
    def parent_children(self) -> List["EntryParent"]:
        """This parent's children that are also parents"""
        return _sort_entries([child for child in self.child_entries if self.is_entry_parent(child)])

    @functools.cache
    def entry_children(self) -> List[Entry]:
        """This parent's children that are entries"""
        return _sort_entries(
            [child.to_type(Entry) for child in self.child_entries if self.is_entry(child)]
        )

    def _playlist_variables(self, idx: int, children: List[TBaseEntry], parent_type: str) -> Dict:
        _count = self.kwargs_get(PLAYLIST_COUNT, len(children))
        _index = children[idx].kwargs_get(PLAYLIST_INDEX, idx + 1)

        if parent_type == ParentType.SOURCE:
            return {SOURCE_INDEX: _index, SOURCE_COUNT: _count}
        return {
            SOURCE_INDEX: self.kwargs_get(SOURCE_INDEX, 1),
            SOURCE_COUNT: self.kwargs_get(SOURCE_INDEX, 1),
            PLAYLIST_INDEX: _index,
            PLAYLIST_COUNT: _count,
        }

    def _parent_variables(self, parent_type: str) -> Dict:
        def _(source_key: str, playlist_key: str) -> str:
            return playlist_key if parent_type == ParentType.PLAYLIST else source_key

        return {
            _(SOURCE_ENTRY, PLAYLIST_ENTRY): self._kwargs,
            _(SOURCE_TITLE, PLAYLIST_TITLE): self.title,
            _(SOURCE_WEBPAGE_URL, PLAYLIST_WEBPAGE_URL): self.webpage_url,
            _(SOURCE_UID, PLAYLIST_UID): self.uid,
            _(SOURCE_DESCRIPTION, PLAYLIST_DESCRIPTION): self.description,
        }

    def _get_entry_children_variable_list(self, variable_name: str) -> List[str | int]:
        return [getattr(entry_child, variable_name) for entry_child in self.entry_children()]

    def _entry_aggregate_variables(self) -> Dict:
        if not self.entry_children():
            return {}

        return {
            PLAYLIST_MAX_UPLOAD_YEAR: max(self._get_entry_children_variable_list("upload_year")),
            PLAYLIST_MAX_UPLOAD_YEAR_TRUNCATED: max(
                self._get_entry_children_variable_list("upload_year_truncated")
            ),
        }

    # pylint: disable=protected-access

    def _set_child_variables(self, parents: Optional[List["EntryParent"]] = None) -> "EntryParent":
        if parents is None:
            parents = [self]
            self.add_kwargs(
                self._playlist_variables(idx=0, children=parents, parent_type=ParentType.SOURCE)
            )

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

        mergedeep.merge(kwargs_to_add, self._entry_aggregate_variables())
        for idx, entry_child in enumerate(self.entry_children()):
            entry_child.add_kwargs(
                self._playlist_variables(
                    idx=idx, children=self.entry_children(), parent_type=ParentType.PLAYLIST
                )
            )
            entry_child.add_kwargs(kwargs_to_add)

        for idx, parent_child in enumerate(self.parent_children()):
            parent_child.add_kwargs(
                self._playlist_variables(
                    idx=idx, children=self.parent_children(), parent_type=ParentType.SOURCE
                )
            )
            parent_child._set_child_variables(parents=parents + [parent_child])

        return self

    def _read_children_from_entry_dicts(self, entry_dicts: List[Dict]) -> "EntryParent":
        """
        Populates a tree of EntryParents that belong to this instance
        """
        self.child_entries = [
            EntryParent(
                entry_dict=entry_dict,
                working_directory=self.working_directory(),
            )._read_children_from_entry_dicts(entry_dicts)
            for entry_dict in entry_dicts
            if entry_dict in self
        ]
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
    def _get_disconnected_root_parent(
        cls, url: str, parents: List["EntryParent"]
    ) -> Optional["EntryParent"]:
        """
        Sometimes the root-level parent is disconnected via playlist_ids Find it if it exists.
        """

        def _url_matches(webpage_url: str):
            return webpage_url in url or url in webpage_url

        top_level_parents = [
            parent
            for parent in parents
            if not parent.child_entries and _url_matches(parent.webpage_url)
        ]
        if len(top_level_parents) == 0:
            return None

        match len(top_level_parents):
            case 0:
                return None
            case 1:
                return top_level_parents[0]
            case _:
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
            root_parent.child_entries = parents
            parents = [root_parent]

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
