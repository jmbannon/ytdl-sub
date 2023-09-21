from ytdl_sub.entries.entry import Entry
from ytdl_sub.script.types.resolvable import Boolean
from ytdl_sub.script.types.resolvable import Resolvable
from ytdl_sub.script.types.resolvable import String


class SpecialFunctions:
    @staticmethod
    def if_(condition: Boolean, true: Resolvable, false: Resolvable) -> Resolvable:
        if condition.value:
            return true
        return false

    @staticmethod
    def entry_contains(entry: Entry, key: String) -> Boolean:
        return Boolean(entry.kwargs_contains(key=key.value))

    @staticmethod
    def entry(entry: Entry, key: String) -> Resolvable:
        return entry.kwargs(key=key.value)

    @staticmethod
    def entry_get(entry: Entry, key: String, default: Resolvable) -> Resolvable:
        return entry.kwargs_get(key=key.value, default=default.value)
