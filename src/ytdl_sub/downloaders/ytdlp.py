import contextlib
import contextvars
import copy
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Tuple

import yt_dlp as ytdl
from yt_dlp.postprocessor.common import PostProcessor
from yt_dlp.utils import ExistingVideoReached, MaxDownloadsReached, RejectedVideoReached

from ytdl_sub.thread.log_entries_downloaded_listener import LogEntriesDownloadedListener
from ytdl_sub.utils.exceptions import FileNotDownloadedException
from ytdl_sub.utils.logger import Logger


class _EnumerationTracker:
    """
    Tracks entry IDs enumerated by yt-dlp playlists (including entries whose full metadata
    extraction later fails under ``ignoreerrors``) and child playlists whose own enumeration fails.
    """

    def __init__(self) -> None:
        self.enumerated_ids: Set[str] = set()
        self.processed_playlist_ids: Set[str] = set()
        self._referenced_playlists: Set[str] = set()

    @staticmethod
    def _is_playlist_reference(entry: Dict, downloader: Optional[ytdl.YoutubeDL]) -> bool:
        if downloader is None or entry.get("_type", "video") not in ("url", "url_transparent"):
            return False

        ie_key = entry.get("ie_key")
        url = entry.get("url")
        if not ie_key or not url:
            return False

        try:
            extractor = downloader.get_info_extractor(ie_key)
        except Exception:  # pylint: disable=broad-except
            return False

        if extractor is None:
            return False

        single_video = extractor.is_single_video(url)
        return single_video is False or (single_video is None and ie_key == "YoutubeTab")

    def record_playlist_info(self, info: Dict, downloader: Optional[ytdl.YoutubeDL] = None) -> None:
        """
        Records entry IDs from a processed playlist dict and tracks referenced sub-playlists.
        """
        if playlist_id := info.get("id"):
            self.processed_playlist_ids.add(str(playlist_id))

        for entry in info.get("entries") or []:
            self.record_entry(entry=entry, downloader=downloader)

    def record_entry(self, entry: Dict, downloader: Optional[ytdl.YoutubeDL] = None) -> None:
        """
        Records a playlist item ID or nested playlist entries.
        """
        if not isinstance(entry, dict):
            return

        entry_type = entry.get("_type", "video")
        if entry_type in ("playlist", "multi_video"):
            self.record_playlist_info(info=entry, downloader=downloader)
            return

        entry_id = entry.get("id")
        if self._is_playlist_reference(entry=entry, downloader=downloader):
            label = str(entry_id or entry.get("url") or "unknown")
            self._referenced_playlists.add(label)
            return

        if entry_id:
            self.enumerated_ids.add(str(entry_id))

    def unprocessed_referenced_playlists(self) -> List[str]:
        """
        Returns referenced child playlists whose own playlist processing never completed.
        """
        return sorted(self._referenced_playlists - self.processed_playlist_ids)

    def finalize(
        self,
        extract_info_result: Optional[Dict],
        has_entry_dicts: bool,
        truncated: bool,
        truncation_reasons: Optional[List[str]],
        enumerated_entry_ids: Optional[Set[str]],
    ) -> None:
        """
        Applies fallback inspection when extract_info was stubbed, propagates playlist
        enumeration failures to truncation_reasons, and exports enumerated IDs.
        """
        if not truncated:
            if not self.processed_playlist_ids and isinstance(extract_info_result, dict):
                self.record_entry(entry=extract_info_result, downloader=None)

            if truncation_reasons is not None:
                if extract_info_result is None and not has_entry_dicts:
                    truncation_reasons.append("ExtractionFailed")
                for missing_playlist in self.unprocessed_referenced_playlists():
                    truncation_reasons.append(f"PlaylistExtractionFailed:{missing_playlist}")

        if enumerated_entry_ids is not None:
            enumerated_entry_ids.update(self.enumerated_ids)


class _PlaylistEnumerationPostProcessor(PostProcessor):
    def __init__(self, downloader: ytdl.YoutubeDL, tracker: _EnumerationTracker) -> None:
        super().__init__(downloader=downloader)
        self._tracker = tracker

    def run(self, information: Dict) -> Tuple[List[str], Dict]:
        self._tracker.record_playlist_info(info=information, downloader=self._downloader)
        return [], information


_ENUMERATION_TRACKER: contextvars.ContextVar[Optional[_EnumerationTracker]] = (
    contextvars.ContextVar("ytdl_sub_enumeration_tracker", default=None)
)


class YTDLP:
    _EXTRACT_ENTRY_NUM_RETRIES: int = 5
    _EXTRACT_ENTRY_RETRY_WAIT_SEC: int = 5

    logger = Logger.get(name="yt-dlp-downloader")

    @classmethod
    @contextmanager
    def ytdlp_downloader(cls, ytdl_options_overrides: Dict) -> ytdl.YoutubeDL:
        """
        Context manager to interact with yt_dlp.
        """
        cls.logger.debug("ytdl_options: %s", str(ytdl_options_overrides))
        with Logger.handle_external_logs(name="yt-dlp"):
            # Deep copy ytdl_options in case yt-dlp modifies the dict
            with ytdl.YoutubeDL(copy.deepcopy(ytdl_options_overrides)) as ytdl_downloader:
                if (tracker := _ENUMERATION_TRACKER.get()) is not None:
                    ytdl_downloader.add_post_processor(
                        _PlaylistEnumerationPostProcessor(
                            downloader=ytdl_downloader, tracker=tracker
                        ),
                        when="playlist",
                    )
                yield ytdl_downloader

    @classmethod
    def extract_info(cls, ytdl_options_overrides: Dict, **kwargs) -> Dict:
        """
        Wrapper around yt_dlp.YoutubeDL.YoutubeDL.extract_info
        All kwargs will passed to the extract_info function.

        Parameters
        ----------
        ytdl_options_overrides
            Optional. Dict containing ytdl args to override other predefined ytdl args
        **kwargs
            arguments passed directory to YoutubeDL extract_info
        """
        with cls.ytdlp_downloader(ytdl_options_overrides) as ytdlp:
            return ytdlp.extract_info(**kwargs)

    @classmethod
    def extract_info_with_retry(
        cls,
        ytdl_options_overrides: Dict,
        is_downloaded_fn: Optional[Callable[[], bool]] = None,
        is_thumbnail_downloaded_fn: Optional[Callable[[], bool]] = None,
        **kwargs,
    ) -> Dict:
        """
        Wrapper around yt_dlp.YoutubeDL.YoutubeDL.extract_info
        All kwargs will passed to the extract_info function.

        This should be used when downloading a single entry. Checks if the entry's video
        and thumbnail files exist - retry if they do not.

        Parameters
        ----------
        ytdl_options_overrides
            Dict containing ytdl args to override other predefined ytdl args
        is_downloaded_fn
            Optional. Function to check if the entry is downloaded
        is_thumbnail_downloaded_fn
            Optional. Function to check if the entry thumbnail is downloaded
        **kwargs
            arguments passed directory to YoutubeDL extract_info

        Raises
        ------
        FileNotDownloadedException
            If the entry fails to download
        """
        num_tries = 0
        copied_ytdl_options_overrides = copy.deepcopy(ytdl_options_overrides)

        is_downloaded = False
        entry_dict: Optional[Dict] = None

        while num_tries < cls._EXTRACT_ENTRY_NUM_RETRIES:
            entry_dict = cls.extract_info(
                ytdl_options_overrides=copied_ytdl_options_overrides, **kwargs
            )

            is_downloaded = is_downloaded_fn is None or is_downloaded_fn()
            is_thumbnail_downloaded = (
                is_thumbnail_downloaded_fn is None or is_thumbnail_downloaded_fn()
            )

            if is_downloaded and is_thumbnail_downloaded:
                return entry_dict or {}  # in-case yt-dlp returns None

            # Always add check_formats
            # See https://github.com/yt-dlp/yt-dlp/issues/502
            copied_ytdl_options_overrides["check_formats"] = True

            # If the video file is downloaded but the thumbnail is not, then do not download
            # the video again
            if is_downloaded and not is_thumbnail_downloaded:
                copied_ytdl_options_overrides["skip_download"] = True
                copied_ytdl_options_overrides["writethumbnail"] = True

            time.sleep(cls._EXTRACT_ENTRY_RETRY_WAIT_SEC)
            num_tries += 1

            # Remove the download archive to retry without thinking its already downloaded,
            # even though it is not
            if "download_archive" in copied_ytdl_options_overrides:
                del copied_ytdl_options_overrides["download_archive"]

            if num_tries < cls._EXTRACT_ENTRY_NUM_RETRIES:
                cls.logger.debug(
                    "Failed to download entry. Retrying %d / %d",
                    num_tries,
                    cls._EXTRACT_ENTRY_NUM_RETRIES,
                )

        # Still return if the media file downloaded (thumbnail could be missing)
        if is_downloaded and entry_dict is not None:
            return entry_dict

        error_dict = {"ytdl_options": ytdl_options_overrides, "kwargs": kwargs}
        raise FileNotDownloadedException(
            f"yt-dlp failed to download an entry with these arguments: {error_dict}"
        )

    @classmethod
    def _get_entry_dicts_from_info_json_files(cls, working_directory: str) -> List[Dict]:
        """
        Parameters
        ----------
        working_directory
            Directory that info json files are located

        Returns
        -------
        List of all info.json files read as JSON dicts
        """
        entry_dicts: List[Dict] = []
        info_json_paths = [
            Path(working_directory) / file_name
            for file_name in os.listdir(working_directory)
            if file_name.endswith(".info.json")
        ]

        for info_json_path in info_json_paths:
            with open(info_json_path, "r", encoding="utf-8") as file:
                entry_dicts.append(json.load(file))

        return entry_dicts

    @classmethod
    @contextlib.contextmanager
    def _listen_and_log_downloaded_info_json(
        cls, working_directory: str, log_prefix: Optional[str]
    ):
        """
        Context manager that starts a separate thread that listens for new .info.json files,
        prints their titles as they appear
        """
        if not log_prefix:
            yield
            return

        info_json_listener = LogEntriesDownloadedListener(
            working_directory=working_directory,
            log_prefix=log_prefix,
        )

        info_json_listener.start()

        try:
            yield
        finally:
            info_json_listener.complete = True

    @classmethod
    def _collect_parent_entry_dicts(
        cls, entry_dicts: List[Dict], ytdl_options_overrides: Dict
    ) -> List[Dict]:
        """
        Fetches additional uploader metadata dicts not fetched in a single playlist request.
        """
        parent_dicts: List[Dict] = []
        entry_ids = {entry_dict.get("id") for entry_dict in entry_dicts}

        for entry_dict in entry_dicts:
            if not (uploader_id := entry_dict.get("uploader_id")):
                continue
            if uploader_id in entry_ids or not (uploader_url := entry_dict.get("uploader_url")):
                continue

            cls.logger.debug("Attempting to get parent metadata from URL %s", uploader_url)
            parent_dict: Optional[Dict] = None
            try:
                parent_dict = cls.extract_info(
                    ytdl_options_overrides=ytdl_options_overrides | {"playlist_items": "0:0"},
                    url=uploader_url,
                )
            except Exception:  # pylint: disable=broad-except
                cls.logger.debug(
                    "Failed to get parent metadata from URL %s", uploader_url, exc_info=True
                )

            parent_id = parent_dict.get("id") if isinstance(parent_dict, dict) else None
            if parent_id and parent_id not in entry_ids:
                parent_dicts.append(parent_dict)
                entry_ids.add(parent_id)
                cls.logger.debug("Adding parent metadata with ids [%s, %s]", uploader_id, parent_id)

            # Always add the uploader_id since it has been tried
            entry_ids.add(uploader_id)

        return parent_dicts

    @classmethod
    def extract_info_via_info_json(
        cls,
        working_directory: str,
        ytdl_options_overrides: Dict,
        log_prefix_on_info_json_dl: Optional[str] = None,
        truncation_reasons: Optional[List[str]] = None,
        enumerated_entry_ids: Optional[Set[str]] = None,
        **kwargs,
    ) -> List[Dict]:
        """
        Wrapper around yt_dlp.YoutubeDL.YoutubeDL.extract_info with infojson enabled. Entry dicts
        are extracted via reading all info.json files in the working directory rather than
        from the output of extract_info.

        This allows us to catch RejectedVideoReached and ExistingVideoReached exceptions, and
        simply ignore while still being able to read downloaded entry metadata.

        Parameters
        ----------
        working_directory
            Directory that info json files reside in
        ytdl_options_overrides
            Dict containing ytdl args to override other predefined ytdl args
        log_prefix_on_info_json_dl
            Optional. Spin a new thread to listen for new info.json files. Log
            f'{log_prefix_on_info_json_dl} {title}' when a new one appears
        truncation_reasons
            Optional. Appends the name of any exception that stopped metadata
            collection early. A non-empty list means the returned entries are
            an incomplete view of the source.
        enumerated_entry_ids
            Optional. Updated with entry IDs enumerated across processed playlists
            (including items whose full metadata extraction failed under ignoreerrors).
        **kwargs
            arguments passed directory to YoutubeDL extract_info
        """
        tracker = _EnumerationTracker()
        tracker_token = _ENUMERATION_TRACKER.set(tracker)
        extract_info_result: Optional[Dict] = None
        top_level_threw_truncation = False
        try:
            with cls._listen_and_log_downloaded_info_json(
                working_directory=working_directory, log_prefix=log_prefix_on_info_json_dl
            ):
                extract_info_result = cls.extract_info(
                    ytdl_options_overrides=ytdl_options_overrides, **kwargs
                )
        except RejectedVideoReached:
            top_level_threw_truncation = True
            if truncation_reasons is not None:
                truncation_reasons.append("RejectedVideoReached")
            cls.logger.debug(
                "RejectedVideoReached, stopping additional downloads "
                "(Can be disable by setting `date_range.breaks` to False)."
            )
        except ExistingVideoReached:
            top_level_threw_truncation = True
            if truncation_reasons is not None:
                truncation_reasons.append("ExistingVideoReached")
            cls.logger.debug(
                "ExistingVideoReached, stopping additional downloads. "
                "(Can be disable by setting `ytdl_options.break_on_existing` to False)."
            )
        except MaxDownloadsReached:
            top_level_threw_truncation = True
            if truncation_reasons is not None:
                truncation_reasons.append("MaxDownloadsReached")
            cls.logger.info("MaxDownloadsReached, stopping additional downloads.")
        finally:
            _ENUMERATION_TRACKER.reset(tracker_token)

        entry_dicts = cls._get_entry_dicts_from_info_json_files(working_directory=working_directory)
        tracker.finalize(
            extract_info_result=extract_info_result,
            has_entry_dicts=bool(entry_dicts),
            truncated=top_level_threw_truncation,
            truncation_reasons=truncation_reasons,
            enumerated_entry_ids=enumerated_entry_ids,
        )
        parent_dicts = cls._collect_parent_entry_dicts(
            entry_dicts=entry_dicts,
            ytdl_options_overrides=ytdl_options_overrides,
        )
        return entry_dicts + parent_dicts
