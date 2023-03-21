import copy
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict
from typing import Iterable
from typing import List

from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.downloaders.base_downloader import BaseDownloader
from ytdl_sub.downloaders.base_downloader import BaseDownloaderOptionsT
from ytdl_sub.downloaders.base_downloader import BaseDownloaderValidator
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import get_file_extension
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadMapping
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class InfoJsonDownloaderOptions(BaseDownloaderValidator):
    _optional_keys = {"no-op"}


class InfoJsonDownloader(BaseDownloader[InfoJsonDownloaderOptions]):
    downloader_options_type = InfoJsonDownloaderOptions

    def __init__(
        self,
        download_options: BaseDownloaderOptionsT,
        enhanced_download_archive: EnhancedDownloadArchive,
        download_ytdl_options: YTDLOptionsBuilder,
        metadata_ytdl_options: YTDLOptionsBuilder,
        overrides: Overrides,
    ):
        super().__init__(
            download_options=download_options,
            enhanced_download_archive=enhanced_download_archive,
            download_ytdl_options=download_ytdl_options,
            metadata_ytdl_options=metadata_ytdl_options,
            overrides=overrides,
        )
        # Keep track of original file mappings for the 'mock' download
        self._original_mapping = copy.deepcopy(enhanced_download_archive.mapping)

    @property
    def output_directory(self) -> str:
        """
        Returns
        -------
        The output directory
        """
        return self._enhanced_download_archive.output_directory

    def _get_entry_from_download_mapping(self, download_mapping: DownloadMapping):
        """
        Try to load an entry from a download mapping's info json
        """
        for file_name in download_mapping.file_names:
            if file_name.endswith(".info.json"):
                try:
                    with open(
                        Path(self.output_directory) / file_name, "r", encoding="utf-8"
                    ) as maybe_info_json:
                        entry_dict = json.load(maybe_info_json)
                except Exception as exc:
                    raise ValidationException(
                        "info.json file cannot be loaded - subscription cannot be reformatted"
                    ) from exc

                return Entry(
                    entry_dict=entry_dict,
                    working_directory=self.working_directory,
                )

        raise ValidationException(
            "info.json file could not be found - subscription cannot be reformatted"
        )

    def download_metadata(self) -> Iterable[Entry]:
        """
        Loads all entries via their info.json files first (to ensure they are all valid), then
        iterates them
        """
        # Track to see if files were modified
        file_names_mtime: Dict[str, Dict[str, float]] = defaultdict(dict)
        entries: List[Entry] = []

        for download_mapping in self._enhanced_download_archive.mapping.entry_mappings.values():
            entry = self._get_entry_from_download_mapping(download_mapping)
            entries.append(entry)

            for file_name in download_mapping.file_names:
                file_path = Path(self.output_directory) / file_name
                file_names_mtime[entry.ytdl_uid()][file_name] = os.path.getmtime(file_path)

        for entry in entries:
            # Remove the entry from the live download archive since it will get re-added
            # unless it is filtered
            self._enhanced_download_archive.mapping.remove_entry(entry.uid)

            yield entry

            # If the entry file_path is unchanged, then delete it since it was not part of the
            # reformat output
            for file_name, mtime in file_names_mtime[entry.ytdl_uid()].items():
                if os.path.getmtime(Path(self.output_directory) / file_name) == mtime:
                    self._enhanced_download_archive._file_handler.delete_file_from_output_directory(
                        file_name
                    )

    def download(self, entry: Entry) -> Entry:
        """
        Mock the download by copying the entry file from the output directory into
        the working directory
        """
        # Use original mapping since the live mapping gets wiped
        entry_file_names = self._original_mapping.entry_mappings[entry.uid].file_names

        for file_name in entry_file_names:
            ext = get_file_extension(file_name)
            file_path = Path(self.output_directory) / file_name
            working_directory_file_path = Path(self.working_directory) / f"{entry.uid}.{ext}"

            # NFO files will always get rewritten, so ignore
            if ext == "nfo":
                continue

            if not self.is_dry_run:
                FileHandler.copy(
                    src_file_path=file_path,
                    dst_file_path=working_directory_file_path,
                )

        return entry
