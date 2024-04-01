import copy
import json
from pathlib import Path
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.config.validators.options import OptionsDictValidator
from ytdl_sub.downloaders.source_plugin import SourcePlugin
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.script.variable_definitions import VARIABLE_SCRIPTS
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.file_handler import get_file_extension
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadMapping
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

v: VariableDefinitions = VARIABLES


class InfoJsonDownloaderOptions(OptionsDictValidator):
    _optional_keys = {"no-op"}


class InfoJsonDownloader(SourcePlugin[InfoJsonDownloaderOptions]):
    plugin_options_type = InfoJsonDownloaderOptions

    def __init__(
        self,
        options: InfoJsonDownloaderOptions,
        enhanced_download_archive: EnhancedDownloadArchive,
        download_ytdl_options: YTDLOptionsBuilder,
        metadata_ytdl_options: YTDLOptionsBuilder,
        overrides: Overrides,
    ):
        super().__init__(
            options=options,
            enhanced_download_archive=enhanced_download_archive,
            download_ytdl_options=download_ytdl_options,
            metadata_ytdl_options=metadata_ytdl_options,
            overrides=overrides,
        )
        # Keep track of original file mappings for the 'mock' download
        self._original_entry_mappings = copy.deepcopy(
            enhanced_download_archive.mapping.entry_mappings
        )

    @property
    def output_directory(self) -> str:
        """
        Returns
        -------
        The output directory
        """
        return self._enhanced_download_archive.output_directory

    @property
    def _entry_mappings(self) -> Dict[str, DownloadMapping]:
        """
        Returns
        -------
        The up-to-date entry mappings
        """
        return self._enhanced_download_archive.mapping.entry_mappings

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
        entries: List[Entry] = []

        for download_mapping in self._enhanced_download_archive.mapping.entry_mappings.values():
            entry = self._get_entry_from_download_mapping(download_mapping)

            # See if prior variables exist. If so, delete them from metadata
            # to avoid saving them recursively on multiple updates
            prior_variables = entry.maybe_get_prior_variables()

            entry.initialize_script(self.overrides).add(
                {
                    inj: prior_variables.get(
                        inj.variable_name,
                        VARIABLE_SCRIPTS[inj.variable_name],
                    )
                    for inj in v.injected_variables()
                }
            )
            entries.append(entry)

        # TODO: MATCH A URL TO A URL_VALIDATOR !!!
        for entry in sorted(entries, key=lambda ent: ent.get(v.download_index, int)):
            # Remove each entry from the live download archive since it will get re-added
            # unless it is filtered
            self._enhanced_download_archive.mapping.remove_entry(entry.uid)
            yield entry

            # If the original entry file_path is no longer maintained in the new mapping, then
            # delete it
            num_original_files_deleted: int = 0
            for file_name in self._original_entry_mappings[entry.uid].file_names:
                if (
                    entry.uid not in self._entry_mappings
                    or file_name not in self._entry_mappings[entry.uid].file_names
                ):
                    num_original_files_deleted += 1
                    self._enhanced_download_archive.delete_file_from_output_directory(file_name)

            # If all original entry files are deleted, mark it as deleted
            if num_original_files_deleted == len(
                self._original_entry_mappings[entry.uid].file_names
            ):
                self._enhanced_download_archive.num_entries_removed += 1

    def download(self, entry: Entry) -> Optional[Entry]:
        """
        Mock the download by copying the entry file from the output directory into
        the working directory
        """
        # Use original mapping since the live mapping gets wiped
        entry_file_names = self._original_entry_mappings[entry.uid].file_names

        for file_name in entry_file_names:
            ext = get_file_extension(file_name)
            file_path = Path(self.output_directory) / file_name
            working_directory_file_path = Path(self.working_directory) / entry.base_filename(
                ext=ext
            )

            # NFO files will always get rewritten, so ignore
            if ext == "nfo":
                continue

            if not self.is_dry_run:
                FileHandler.copy(
                    src_file_path=file_path,
                    dst_file_path=working_directory_file_path,
                )

        return entry
