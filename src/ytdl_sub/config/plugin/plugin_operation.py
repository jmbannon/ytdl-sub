from enum import Enum


class PluginOperation(Enum):
    DOWNLOADER = -1
    MODIFY_ENTRY_METADATA = 0
    MODIFY_ENTRY = 1
    POST_PROCESS = 2
