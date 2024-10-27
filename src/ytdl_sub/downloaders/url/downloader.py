import contextlib
import os
from pathlib import Path
from typing import Dict
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from yt_dlp.utils import RejectedVideoReached

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.downloaders.source_plugin import SourcePlugin
from ytdl_sub.downloaders.source_plugin import SourcePluginExtension
from ytdl_sub.downloaders.url.validators import MultiUrlValidator
from ytdl_sub.downloaders.url.validators import UrlThumbnailListValidator
from ytdl_sub.downloaders.url.validators import UrlValidator
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.entry_parent import EntryParent
from ytdl_sub.entries.script.variable_definitions import VARIABLES
from ytdl_sub.entries.script.variable_definitions import VariableDefinitions
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.script import ScriptUtils
from ytdl_sub.utils.thumbnail import ThumbnailTypes
from ytdl_sub.utils.thumbnail import download_and_convert_url_thumbnail
from ytdl_sub.utils.thumbnail import try_convert_download_thumbnail
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

v: VariableDefinitions = VARIABLES

download_logger = Logger.get(name="downloader")


class URLDownloadState:
    def __init__(self, entries_total: int):
        self.entries_total = entries_total
        self.entries_downloaded = 0


class UrlDownloaderBasePluginExtension(SourcePluginExtension[MultiUrlValidator]):
    def _match_entry_to_url_validator(self, entry: Entry) -> UrlValidator:
        """
        Handle matching a URL to its original validator. This is for .info.json updates
        when older entries have missing variables
        """
        input_url_idx = entry.get(v.ytdl_sub_input_url_index, int)
        entry_input_url = entry.get(v.ytdl_sub_input_url, str)

        if 0 <= input_url_idx < len(self.plugin_options.urls.list):
            validator = self.plugin_options.urls.list[input_url_idx]
            if self.overrides.apply_formatter(validator.url) == entry_input_url:
                return validator

        # Match the first validator based on the URL, if one exists
        for validator in self.plugin_options.urls.list:
            if self.overrides.apply_formatter(validator.url) == entry_input_url:
                return validator

        # Return the first validator if none exist
        return self.plugin_options.urls.list[0]


class UrlDownloaderThumbnailPlugin(UrlDownloaderBasePluginExtension):
    def __init__(
        self,
        options: MultiUrlValidator,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        super().__init__(
            options=options,
            overrides=overrides,
            enhanced_download_archive=enhanced_download_archive,
        )
        self._thumbnails_downloaded: Set[str] = set()

    def _download_parent_thumbnails(
        self,
        thumbnail_list_info: UrlThumbnailListValidator,
        entry: Entry,
        parent: EntryParent,
    ) -> None:
        """
        Downloads and moves channel avatar and banner images to the output directory.
        """
        for thumbnail_info in thumbnail_list_info.list:
            thumbnail_name = self.overrides.apply_formatter(thumbnail_info.name, entry=entry)
            thumbnail_id = self.overrides.apply_formatter(thumbnail_info.uid)

            # If the thumbnail name is an empty string, completely ignore trying to download it
            if not thumbnail_name:
                continue

            # If latest entry, always update the thumbnail on each entry
            if thumbnail_id == ThumbnailTypes.LATEST_ENTRY:

                # always save in dry-run even if it doesn't exist...
                if self.is_dry_run or entry.is_thumbnail_downloaded():
                    self.save_file(
                        file_name=entry.get_download_thumbnail_name(),
                        output_file_name=thumbnail_name,
                        copy_file=True,
                    )
                    self._thumbnails_downloaded.add(thumbnail_name)
                continue

            # If not latest entry and the thumbnail has already been downloaded, then skip
            if thumbnail_name in self._thumbnails_downloaded:
                continue

            if (thumbnail_url := parent.get_thumbnail_url(thumbnail_id=thumbnail_id)) is None:
                download_logger.debug("Failed to find thumbnail id '%s'", thumbnail_id)
                continue

            if download_and_convert_url_thumbnail(
                thumbnail_url=thumbnail_url,
                output_thumbnail_path=str(Path(self.working_directory) / thumbnail_name),
            ):
                self.save_file(file_name=thumbnail_name)
                self._thumbnails_downloaded.add(thumbnail_name)
            else:
                download_logger.debug("Failed to download thumbnail id '%s'", thumbnail_id)

    def _download_url_thumbnails(self, collection_url: UrlValidator, entry: Entry):
        """
        After all media entries have been downloaded, post processed, and moved to the output
        directory, run this function. This lets the downloader add any extra files directly to the
        output directory, for things like YT channel image, banner.
        """
        if source_metadata := entry.get(v.source_metadata, dict):
            self._download_parent_thumbnails(
                thumbnail_list_info=collection_url.source_thumbnails,
                entry=entry,
                parent=EntryParent(source_metadata, working_directory=self.working_directory),
            )

        if playlist_metadata := entry.get(v.playlist_metadata, dict):
            self._download_parent_thumbnails(
                thumbnail_list_info=collection_url.playlist_thumbnails,
                entry=entry,
                parent=EntryParent(playlist_metadata, working_directory=self.working_directory),
            )

    def modify_entry(self, entry: Entry) -> Optional[Entry]:
        """
        Use the entry to download thumbnails (or move if LATEST_ENTRY).
        In addition, convert the entry thumbnail to jpg
        """
        # We always convert entry thumbnails to jpgs, and is performed here to be done
        # as early as possible in the plugin pipeline (downstream plugins depend on it being jpg)
        if not self.is_dry_run:
            try_convert_download_thumbnail(entry=entry)

        self._download_url_thumbnails(
            collection_url=self._match_entry_to_url_validator(entry=entry),
            entry=entry,
        )
        return entry


class UrlDownloaderCollectionVariablePlugin(UrlDownloaderBasePluginExtension):
    def __init__(
        self,
        options: MultiUrlValidator,
        overrides: Overrides,
        enhanced_download_archive: EnhancedDownloadArchive,
    ):
        super().__init__(
            options=options,
            overrides=overrides,
            enhanced_download_archive=enhanced_download_archive,
        )
        self._thumbnails_downloaded: Set[str] = set()

    def modify_entry_metadata(self, entry: Entry) -> Optional[Entry]:
        """
        Add collection variables to the entry
        """
        collection_url = self._match_entry_to_url_validator(entry=entry)
        entry.add(collection_url.variables.dict_with_format_strings)

        return entry


class MultiUrlDownloader(SourcePlugin[MultiUrlValidator]):
    """
    Class that interacts with ytdl to perform the download of metadata and content,
    and should translate that to list of Entry objects.
    """

    plugin_options_type = MultiUrlValidator
    plugin_extensions = [UrlDownloaderThumbnailPlugin, UrlDownloaderCollectionVariablePlugin]

    @classmethod
    def ytdl_option_defaults(cls) -> Dict:
        """
        .. code-block:: yaml

           ytdl_options:
             ignoreerrors: True  # ignore errors like hidden videos, age restriction, etc
        """
        return {"ignoreerrors": True}

    def __init__(
        self,
        options: MultiUrlValidator,
        enhanced_download_archive: EnhancedDownloadArchive,
        download_ytdl_options: YTDLOptionsBuilder,
        metadata_ytdl_options: YTDLOptionsBuilder,
        overrides: Overrides,
    ):
        """
        Parameters
        ----------
        options
            Options validator for this downloader
        enhanced_download_archive
            Download archive
        download_ytdl_options
            YTDL options builder for downloading media
        metadata_ytdl_options
            YTDL options builder for downloading metadata
        overrides
            Override variables
        """
        super().__init__(
            options=options,
            enhanced_download_archive=enhanced_download_archive,
            download_ytdl_options=download_ytdl_options,
            metadata_ytdl_options=metadata_ytdl_options,
            overrides=overrides,
        )
        self._downloaded_entries: Set[str] = set()
        self._url_state: Optional[URLDownloadState] = None

    def download_ytdl_options(self, url_idx: Optional[int] = None) -> Dict:
        """
        Returns
        -------
        YTLD options dict for downloading
        """
        return (
            self._download_ytdl_options_builder.clone()
            .add(self.ytdl_option_defaults(), before=True)
            .add(
                (
                    self.plugin_options.urls.list[url_idx].ytdl_options.dict
                    if url_idx is not None
                    else None
                ),
                before=True,
            )
            .to_dict()
        )

    def metadata_ytdl_options(self, ytdl_option_overrides: Dict) -> Dict:
        """
        Returns
        -------
        YTDL options dict for fetching metadata
        """

        return (
            self._metadata_ytdl_options_builder.clone()
            .add(self.ytdl_option_defaults(), before=True)
            .add(ytdl_option_overrides, before=True)
            .to_dict()
        )

    @property
    def is_dry_run(self) -> bool:
        """
        Returns
        -------
        True if dry-run is enabled. False otherwise.
        """
        return self.download_ytdl_options().get("skip_download", False)

    @property
    def is_entry_thumbnails_enabled(self) -> bool:
        """
        Returns
        -------
        True if entry thumbnails should be downloaded. False otherwise.
        """
        return self.download_ytdl_options().get("writethumbnail", False)

    ###############################################################################################
    # DOWNLOAD FUNCTIONS

    def _is_downloaded(self, entry: Entry) -> bool:
        return entry.ytdl_uid() in self._downloaded_entries

    def _mark_downloaded(self, entry: Entry) -> None:
        self._downloaded_entries.add(entry.ytdl_uid())

    @property
    def collection(self) -> MultiUrlValidator:
        """Return the download options collection"""
        return self.plugin_options

    @contextlib.contextmanager
    def _separate_download_archives(self, clear_info_json_files: bool = False):
        """
        Separate download archive writing between collection urls. This is so break_on_existing
        does not break when downloading from subset urls.

        Parameters
        ----------
        clear_info_json_files
            Whether to delete info.json files after yield
        """
        archive_path = self.download_ytdl_options().get("download_archive", "")
        backup_archive_path = f"{archive_path}.backup"

        # If archive path exists, maintain download archive is enable
        if archive_file_exists := archive_path and os.path.isfile(archive_path):
            archive_file_exists = True

            # If a backup exists, it's the one prior to any downloading, use that.
            if os.path.isfile(backup_archive_path):
                FileHandler.copy(src_file_path=backup_archive_path, dst_file_path=archive_path)
            # If not, create the backup
            else:
                FileHandler.copy(src_file_path=archive_path, dst_file_path=backup_archive_path)

        yield

        # If an archive path did not exist at first, but now exists, delete it
        if not archive_file_exists and os.path.isfile(archive_path):
            FileHandler.delete(file_path=archive_path)
        # If the archive file did exist, restore the backup
        elif archive_file_exists:
            FileHandler.move(src_file_path=backup_archive_path, dst_file_path=archive_path)

        # Clear info json files if true
        if clear_info_json_files:
            info_json_files = [
                Path(self.working_directory) / path
                for path in os.listdir(self.working_directory)
                if path.endswith(".info.json")
            ]
            for info_json_file in info_json_files:
                FileHandler.delete(info_json_file)

    def _extract_entry_info_with_retry(self, entry: Entry) -> Entry:
        download_entry_dict = YTDLP.extract_info_with_retry(
            ytdl_options_overrides=self.download_ytdl_options(
                url_idx=entry.get(v.ytdl_sub_input_url_index, int)
            ),
            is_downloaded_fn=None if self.is_dry_run else entry.is_downloaded,
            is_thumbnail_downloaded_fn=(
                None
                if (self.is_dry_run or not self.is_entry_thumbnails_enabled)
                else entry.is_thumbnail_downloaded_via_ytdlp
            ),
            url=entry.webpage_url,
        )
        return Entry(
            download_entry_dict,
            working_directory=self.working_directory,
        )

    def _iterate_child_entries(
        self, entries: List[Entry], download_reversed: bool
    ) -> Iterator[Entry]:
        # Iterate a list of entries, and delete the entries after yielding
        entries_to_iter: List[Optional[Entry]] = entries

        indices = list(range(len(entries_to_iter)))
        if download_reversed:
            indices = reversed(indices)

        for idx in indices:
            self._url_state.entries_downloaded += 1

            if self._is_downloaded(entries_to_iter[idx]):
                download_logger.info(
                    "Already downloaded entry %d/%d: %s",
                    self._url_state.entries_downloaded,
                    self._url_state.entries_total,
                    entries_to_iter[idx].title,
                )
                entries_to_iter[idx] = None
                continue

            yield entries_to_iter[idx]
            self._mark_downloaded(entries_to_iter[idx])

            entries_to_iter[idx] = None

    def _iterate_parent_entry(
        self, parent: EntryParent, download_reversed: bool
    ) -> Iterator[Entry]:
        yield from self._iterate_child_entries(
            entries=parent.entry_children(), download_reversed=download_reversed
        )

        # Recursion the parent's parent entries
        for parent_child in reversed(parent.parent_children()):
            yield from self._iterate_parent_entry(
                parent=parent_child, download_reversed=download_reversed
            )

    def _download_url_metadata(
        self, url: str, include_sibling_metadata: bool, ytdl_options_overrides: Dict
    ) -> Tuple[List[EntryParent], List[Entry]]:
        """
        Downloads only info.json files and forms EntryParent trees
        """
        with self._separate_download_archives():
            entry_dicts = YTDLP.extract_info_via_info_json(
                working_directory=self.working_directory,
                ytdl_options_overrides=ytdl_options_overrides,
                log_prefix_on_info_json_dl="Downloading metadata for",
                url=url,
            )

        parents = EntryParent.from_entry_dicts(
            url=url,
            entry_dicts=entry_dicts,
            working_directory=self.working_directory,
            include_sibling_metadata=include_sibling_metadata,
        )
        orphans = EntryParent.from_entry_dicts_with_no_parents(
            parents=parents,
            entry_dicts=entry_dicts,
            working_directory=self.working_directory,
        )

        return parents, orphans

    def _iterate_entries(
        self,
        parents: List[EntryParent],
        orphans: List[Entry],
        download_reversed: bool,
    ) -> Iterator[Entry]:
        """
        Downloads the leaf entries from EntryParent trees
        """
        # Delete info json files afterwards so other collection URLs do not use them
        with self._separate_download_archives(clear_info_json_files=True):
            for parent in parents:
                yield from self._iterate_parent_entry(
                    parent=parent, download_reversed=download_reversed
                )

            yield from self._iterate_child_entries(
                entries=orphans, download_reversed=download_reversed
            )

    def _download_metadata(self, url: str, validator: UrlValidator) -> Iterable[Entry]:
        metadata_ytdl_options = self.metadata_ytdl_options(
            ytdl_option_overrides=validator.ytdl_options.to_native_dict(self.overrides)
        )
        download_reversed = ScriptUtils.bool_formatter_output(
            self.overrides.apply_formatter(validator.download_reverse)
        )

        parents, orphan_entries = self._download_url_metadata(
            url=url,
            include_sibling_metadata=validator.include_sibling_metadata,
            ytdl_options_overrides=metadata_ytdl_options,
        )

        # TODO: Encapsulate this logic into its own class
        self._url_state = URLDownloadState(
            entries_total=sum(parent.num_children() for parent in parents) + len(orphan_entries)
        )

        download_logger.info("Beginning downloads for %s", url)
        yield from self._iterate_entries(
            parents=parents,
            orphans=orphan_entries,
            download_reversed=download_reversed,
        )

    def download_metadata(self) -> Iterable[Entry]:
        """The function to perform the download of all media entries"""
        # download the bottom-most urls first since they are top-priority
        for idx, url_validator in reversed(list(enumerate(self.collection.urls.list))):
            # URLs can be empty. If they are, then skip
            if not (url := self.overrides.apply_formatter(url_validator.url)):
                continue

            for entry in self._download_metadata(url=url, validator=url_validator):
                entry.initialize_script(self.overrides).add(
                    {
                        v.ytdl_sub_input_url: url,
                        v.ytdl_sub_input_url_index: idx,
                        v.ytdl_sub_input_url_count: len(self.collection.urls.list),
                    }
                )

                yield entry

    def download(self, entry: Entry) -> Optional[Entry]:
        """
        Parameters
        ----------
        entry
            Entry to download

        Returns
        -------
        The entry that was downloaded successfully

        Raises
        ------
        RejectedVideoReached
          If a video was rejected and was not from match_filter
        """
        download_logger.info(
            "Downloading entry %d/%d: %s",
            self._url_state.entries_downloaded,
            self._url_state.entries_total,
            entry.title,
        )

        # Match-filters can be applied at the download stage. If the download is rejected,
        # then return None
        try:
            download_entry = self._extract_entry_info_with_retry(entry=entry)
        except RejectedVideoReached:
            download_logger.info("Entry rejected by download match-filter, skipping ..")
            return None

        upload_date_idx = self._enhanced_download_archive.mapping.get_num_entries_with_upload_date(
            upload_date_standardized=entry.get(v.upload_date_standardized, str)
        )
        download_idx = self._enhanced_download_archive.num_entries

        return entry.add_injected_variables(
            download_entry=download_entry,
            download_idx=download_idx,
            upload_date_idx=upload_date_idx,
        )
