from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import TypeVar

from ytdl_sub.entries.base_entry import BaseEntry

TChildEntry = TypeVar("TChildEntry", bound=BaseEntry)


class EntryParent(BaseEntry):
    def __init__(self, entry_dict: Dict, working_directory: str):
        super().__init__(entry_dict=entry_dict, working_directory=working_directory)
        self._child_entries: List[TChildEntry] = []

    # pylint: disable=no-self-use
    def _get_children_entry_variables_to_add(
        self, child_entries: List[TChildEntry]
    ) -> Dict[str, str | int]:
        """
        Adds source variables to the child entry derived from the parent entry.
        """
        if not child_entries:
            return {}

        return {"playlist_max_upload_year": max(entry.upload_year for entry in child_entries)}

    # pylint: enable=no-self-use

    def read_children_from_entry_dicts(
        self, entry_dicts: List[Dict], child_class: Type[TChildEntry]
    ) -> "EntryParent":
        """
        Parameters
        ----------
        entry_dicts
            Entry dicts to look for children from
        child_class
            The class to convert the entry dict to

        Returns
        -------
        List of children
        """
        child_entries: List[TChildEntry] = []

        for entry_dict in entry_dicts:
            if entry_dict.get("playlist_id") == self.uid:
                child_entries.append(
                    child_class(entry_dict=entry_dict, working_directory=self.working_directory())
                )

        child_variables_to_add = self._get_children_entry_variables_to_add(child_entries)
        for child_entry in child_entries:
            child_entry.add_variables(variables_to_add=child_variables_to_add)

        self._child_entries = sorted(
            child_entries, key=lambda entry: entry.kwargs("playlist_index")
        )
        return self

    @property
    def child_entries(self) -> List[TChildEntry]:
        """
        Returns
        -------
        List of child entities
        """
        return self._child_entries

    @property
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

    def __contains__(self, item):
        """
        Returns
        -------
        True if the the item (entry_dict) has the same id as one of the tracks. False otherwise.
        """
        uid: Optional[str] = None
        if isinstance(item, BaseEntry):
            uid = item.uid
        elif isinstance(item, dict):
            uid = item.get("id")

        if uid is not None:
            return any(uid == child_entry.uid for child_entry in self._child_entries)
        return False

    @classmethod
    def from_entry_dicts_with_children(
        cls,
        entry_dicts: List[Dict],
        working_directory: str,
        child_class: Type[TChildEntry],
        extractor: Optional[str],
    ) -> "EntryParent":
        """
        Load the parent entry and its children
        """
        entry_parent: EntryParent = cls.from_entry_dicts(
            entry_dicts=entry_dicts, working_directory=working_directory, extractor=extractor
        )
        entry_parent.read_children_from_entry_dicts(
            entry_dicts=entry_dicts, child_class=child_class
        )
        return entry_parent
