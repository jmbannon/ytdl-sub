import json
import os.path
import threading
import time
from json import JSONDecodeError
from pathlib import Path
from typing import Optional
from typing import Set

from ytdl_sub.utils.logger import Logger

logger = Logger.get(name="downloader")


class LogEntriesDownloadedListener(threading.Thread):
    def __init__(self, working_directory: str, log_prefix: str):
        """
        To be ran in a thread while download via ytdl-sub. Listens for new .info.json files in the
        working directory, checks the extractor value, and if it matches the input arg, log the
        title.

        Parameters
        ----------
        working_directory
            subscription download working directory
        log_prefix
            The message to print prefixed to the title, i.e. '{log_prefix} {title}'
        """
        threading.Thread.__init__(self)
        self.working_directory = working_directory
        self.log_prefix = log_prefix
        self.complete = False

        self._files_read: Set[str] = set()

    @classmethod
    def _get_title_from_info_json(cls, path: Path) -> Optional[str]:
        try:
            with open(path, "r", encoding="utf-8") as file:
                file_json = json.load(file)
        except JSONDecodeError:
            # swallow the error since this is only printing logs
            return None

        return file_json.get("title")

    @classmethod
    def _is_info_json(cls, path: Path) -> bool:
        if path.is_file():
            _, ext = os.path.splitext(path)
            return ext == ".json"
        return False

    def loop(self) -> None:
        """
        Read new files in the directory and print their titles
        """
        for path in Path(self.working_directory).rglob("*"):
            if path.name not in self._files_read and self._is_info_json(path):
                title = self._get_title_from_info_json(path)
                self._files_read.add(path.name)
                if title:
                    logger.info("%s %s", self.log_prefix, title)

    def run(self):
        """
        Loops over new files and prints their titles
        """
        while not self.complete:
            self.loop()
            time.sleep(0.1)
