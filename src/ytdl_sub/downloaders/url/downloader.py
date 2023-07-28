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

from ytdl_sub.config.plugin import PluginPriority
from ytdl_sub.config.preset_options import Overrides
from ytdl_sub.downloaders.source_plugin import SourcePlugin
from ytdl_sub.downloaders.source_plugin import SourcePluginExtension
from ytdl_sub.downloaders.url.validators import MultiUrlValidator
from ytdl_sub.downloaders.url.validators import UrlThumbnailListValidator
from ytdl_sub.downloaders.url.validators import UrlValidator
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.entries.entry import Entry
from ytdl_sub.entries.entry_parent import EntryParent
from ytdl_sub.entries.variables.kwargs import COLLECTION_URL
from ytdl_sub.entries.variables.kwargs import COMMENTS
from ytdl_sub.entries.variables.kwargs import DOWNLOAD_INDEX
from ytdl_sub.entries.variables.kwargs import PLAYLIST_ENTRY
from ytdl_sub.entries.variables.kwargs import REQUESTED_SUBTITLES
from ytdl_sub.entries.variables.kwargs import SOURCE_ENTRY
from ytdl_sub.entries.variables.kwargs import SPONSORBLOCK_CHAPTERS
from ytdl_sub.entries.variables.kwargs import UPLOAD_DATE_INDEX
from ytdl_sub.entries.variables.kwargs import YTDL_SUB_MATCH_FILTER_REJECT
from ytdl_sub.utils.file_handler import FileHandler
from ytdl_sub.utils.logger import Logger
from ytdl_sub.utils.thumbnail import ThumbnailTypes
from ytdl_sub.utils.thumbnail import download_and_convert_url_thumbnail
from ytdl_sub.utils.thumbnail import try_convert_download_thumbnail
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive

download_logger = Logger.get(name="downloader")


class URLDownloadState:
    def __init__(self, entries_total: int):
        self.entries_total = entries_total
        self.entries_downloaded = 0


class UrlDownloaderThumbnailPlugin(SourcePluginExtension):
    priority = PluginPriority(modify_entry=0)

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
        self._collection_url_mapping: Dict[str, UrlValidator] = {
            self.overrides.apply_formatter(collection_url.url): collection_url
            for collection_url in options.urls.list
        }

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
        if entry.kwargs_contains(PLAYLIST_ENTRY):
            self._download_parent_thumbnails(
                thumbnail_list_info=collection_url.playlist_thumbnails,
                entry=entry,
                parent=EntryParent(
                    entry.kwargs(PLAYLIST_ENTRY), working_directory=self.working_directory
                ),
            )

        if entry.kwargs_contains(SOURCE_ENTRY):
            self._download_parent_thumbnails(
                thumbnail_list_info=collection_url.source_thumbnails,
                entry=entry,
                parent=EntryParent(
                    entry.kwargs(SOURCE_ENTRY), working_directory=self.working_directory
                ),
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

        if entry.kwargs_get(COLLECTION_URL) in self._collection_url_mapping:
            self._download_url_thumbnails(
                collection_url=self._collection_url_mapping[entry.kwargs(COLLECTION_URL)],
                entry=entry,
            )
        return entry


class UrlDownloaderCollectionVariablePlugin(SourcePluginExtension):
    priority = PluginPriority(modify_entry_metadata=0)

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
        self._collection_url_mapping: Dict[str, UrlValidator] = {
            self.overrides.apply_formatter(collection_url.url): collection_url
            for collection_url in options.urls.list
        }

    def modify_entry_metadata(self, entry: Entry) -> Optional[Entry]:
        """
        Add collection variables to the entry
        """
        # COLLECTION_URL is a recent variable that may not exist for old entries when updating.
        # Try to use source_webpage_url if it does not exist
        entry_collection_url = entry.kwargs_get(COLLECTION_URL, entry.source_webpage_url)

        # If the collection URL cannot find its mapping, use the last URL
        collection_url = (
            self._collection_url_mapping.get(entry_collection_url)
            or list(self._collection_url_mapping.values())[-1]
        )

        entry.add_variables(variables_to_add=collection_url.variables.dict_with_format_strings)

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

    @property
    def download_ytdl_options(self) -> Dict:
        """
        Returns
        -------
        YTLD options dict for downloading
        """
        return (
            self._download_ytdl_options_builder.clone()
            .add(self.ytdl_option_defaults(), before=True)
            .to_dict()
        )

    @property
    def metadata_ytdl_options(self) -> Dict:
        """
        Returns
        -------
        YTDL options dict for fetching metadata
        """
        return (
            self._metadata_ytdl_options_builder.clone()
            .add(self.ytdl_option_defaults(), before=True)
            .to_dict()
        )

    @property
    def is_dry_run(self) -> bool:
        """
        Returns
        -------
        True if dry-run is enabled. False otherwise.
        """
        return self.download_ytdl_options.get("skip_download", False)

    @property
    def is_entry_thumbnails_enabled(self) -> bool:
        """
        Returns
        -------
        True if entry thumbnails should be downloaded. False otherwise.
        """
        return self.download_ytdl_options.get("writethumbnail", False)

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
        archive_path = self.download_ytdl_options.get("download_archive", "")
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
            ytdl_options_overrides=self.download_ytdl_options,
            is_downloaded_fn=None if self.is_dry_run else entry.is_downloaded,
            is_thumbnail_downloaded_fn=None
            if (self.is_dry_run or not self.is_entry_thumbnails_enabled)
            else entry.is_thumbnail_downloaded_via_ytdlp,
            url=entry.webpage_url,
        )
        return Entry(download_entry_dict, working_directory=self.working_directory)

    def _iterate_child_entries(
        self, url_validator: UrlValidator, entries: List[Entry]
    ) -> Iterator[Entry]:
        entries_to_iterate = entries
        if url_validator.download_reverse:
            entries_to_iterate = reversed(entries)

        for entry in entries_to_iterate:
            self._url_state.entries_downloaded += 1

            if self._is_downloaded(entry):
                download_logger.info(
                    "Already downloaded entry %d/%d: %s",
                    self._url_state.entries_downloaded,
                    self._url_state.entries_total,
                    entry.title,
                )
                continue

            yield entry
            self._mark_downloaded(entry)

    def _iterate_parent_entry(
        self, url_validator: UrlValidator, parent: EntryParent
    ) -> Iterator[Entry]:
        for entry_child in self._iterate_child_entries(
            url_validator=url_validator, entries=parent.entry_children()
        ):
            yield entry_child

        # Recursion the parent's parent entries
        for parent_child in reversed(parent.parent_children()):
            for entry_child in self._iterate_parent_entry(
                url_validator=url_validator, parent=parent_child
            ):
                yield entry_child

    def _download_url_metadata(self, url: str) -> Tuple[List[EntryParent], List[Entry]]:
        """
        Downloads only info.json files and forms EntryParent trees
        """
        with self._separate_download_archives():
            entry_dicts = YTDLP.extract_info_via_info_json(
                working_directory=self.working_directory,
                ytdl_options_overrides=self.metadata_ytdl_options,
                log_prefix_on_info_json_dl="Downloading metadata for",
                url=url,
            )

        parents = EntryParent.from_entry_dicts(
            url=url,
            entry_dicts=entry_dicts,
            working_directory=self.working_directory,
        )
        orphans = EntryParent.from_entry_dicts_with_no_parents(
            parents=parents, entry_dicts=entry_dicts, working_directory=self.working_directory
        )

        return parents, orphans

    def _iterate_entries(
        self,
        url_validator: UrlValidator,
        parents: List[EntryParent],
        orphans: List[Entry],
    ) -> Iterator[Entry]:
        """
        Downloads the leaf entries from EntryParent trees
        """
        # Delete info json files afterwards so other collection URLs do not use them
        with self._separate_download_archives(clear_info_json_files=True):
            for parent in parents:
                for entry_child in self._iterate_parent_entry(
                    url_validator=url_validator, parent=parent
                ):
                    yield entry_child

            for orphan in self._iterate_child_entries(url_validator=url_validator, entries=orphans):
                yield orphan

    def download_metadata(self) -> Iterable[Entry]:
        """The function to perform the download of all media entries"""
        # download the bottom-most urls first since they are top-priority
        for collection_url in reversed(self.collection.urls.list):
            # URLs can be empty. If they are, then skip
            if not (url := self.overrides.apply_formatter(collection_url.url)):
                continue

            parents, orphan_entries = self._download_url_metadata(url=url)

            # TODO: Encapsulate this logic into its own class
            self._url_state = URLDownloadState(
                entries_total=sum(parent.num_children() for parent in parents) + len(orphan_entries)
            )

            download_logger.info(
                "Beginning downloads for %s", self.overrides.apply_formatter(collection_url.url)
            )
            for entry in self._iterate_entries(
                url_validator=collection_url, parents=parents, orphans=orphan_entries
            ):
                # Add the collection URL to the info_dict to trace where it came from
                entry.add_kwargs(
                    {COLLECTION_URL: self.overrides.apply_formatter(collection_url.url)}
                )
                yield entry

    def download(self, entry: Entry) -> Entry:
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

        # Match-filters are applied at the download stage (not metadata stage).
        # If the download is rejected, and match_filter is present in the ytdl options,
        # then filter downstream in the match_filter plugin
        try:
            download_entry = self._extract_entry_info_with_retry(entry=entry)
        except RejectedVideoReached:
            if "match_filter" in self.download_ytdl_options:
                entry.add_kwargs({YTDL_SUB_MATCH_FILTER_REJECT: True})
                return entry
            raise

        upload_date_idx = self._enhanced_download_archive.mapping.get_num_entries_with_upload_date(
            upload_date_standardized=entry.upload_date_standardized
        )
        download_idx = self._enhanced_download_archive.num_entries

        entry.add_kwargs(
            {
                # Subtitles are not downloaded in metadata run, only here, so move over
                REQUESTED_SUBTITLES: download_entry.kwargs_get(REQUESTED_SUBTITLES),
                # Same with sponsorblock chapters
                SPONSORBLOCK_CHAPTERS: download_entry.kwargs_get(SPONSORBLOCK_CHAPTERS),
                COMMENTS: download_entry.kwargs_get(COMMENTS),
                # Tracks number of entries downloaded
                DOWNLOAD_INDEX: download_idx,
                # Tracks number of entries with the same upload date to make them unique
                UPLOAD_DATE_INDEX: upload_date_idx,
            }
        )

        return entry
