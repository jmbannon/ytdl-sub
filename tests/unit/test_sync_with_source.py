from unittest.mock import patch

import pytest
import yt_dlp
from yt_dlp.utils import DownloadError

from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.downloaders.ytdlp import YTDLP
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.ytdl_additions.enhanced_download_archive import (
    DownloadMapping,
    DownloadMappings,
    EnhancedDownloadArchive,
)


def _make_archive(tmp_path, mappings_dict, dry_run: bool = False):
    working = tmp_path / "working"
    output = tmp_path / "output"
    working.mkdir()
    output.mkdir()

    archive = EnhancedDownloadArchive(
        file_name="archive.json",
        working_directory=str(working),
        output_directory=str(output),
        dry_run=dry_run,
    )
    archive._download_mapping = DownloadMappings()
    for uid, mapping in mappings_dict.items():
        archive._download_mapping._entry_mappings[uid] = mapping
        for fname in mapping.file_names:
            (output / fname).write_text("content")
    return archive


def _record_source(archive, source_entry_ids):
    for entry_id in source_entry_ids:
        archive.record_source_entry_id(entry_id=entry_id)
    return archive


def _mappings():
    return {
        "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}),
        "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}),
        "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}),
    }


class TestRemoveEntriesNotInSource:
    def test_entry_removed_from_source_is_pruned(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings())
        _record_source(archive, {"id1", "id3"})
        archive.remove_entries_not_in_source()

        assert sorted(archive.mapping.entry_mappings.keys()) == ["id1", "id3"]
        assert not (tmp_path / "output" / "b.mp4").exists()

    def test_entry_still_in_source_is_untouched(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings())
        _record_source(archive, {"id1", "id3"})
        archive.remove_entries_not_in_source()

        assert (tmp_path / "output" / "a.mp4").exists()
        assert (tmp_path / "output" / "c.mp4").exists()
        assert archive.num_entries_removed == 1

    def test_all_entries_in_source_removes_nothing(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings())
        _record_source(archive, {"id1", "id2", "id3"})
        archive.remove_entries_not_in_source()

        assert sorted(archive.mapping.entry_mappings.keys()) == ["id1", "id2", "id3"]
        assert archive.num_entries_removed == 0

    def test_source_with_new_entries_removes_nothing(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings())
        _record_source(archive, {"id1", "id2", "id3", "id4"})
        archive.remove_entries_not_in_source()

        assert sorted(archive.mapping.entry_mappings.keys()) == ["id1", "id2", "id3"]
        assert archive.num_entries_removed == 0

    def test_all_files_for_entry_are_deleted(self, tmp_path):
        mappings = {
            "id1": DownloadMapping(
                "2024-01-01",
                "yt",
                {"a.mp4", "a.nfo", "a-thumb.jpg", "a.info.json"},
            ),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}),
        }
        archive = _make_archive(tmp_path, mappings)
        _record_source(archive, {"id2"})
        archive.remove_entries_not_in_source()

        for file_name in ("a.mp4", "a.nfo", "a-thumb.jpg", "a.info.json"):
            assert not (tmp_path / "output" / file_name).exists()
        assert (tmp_path / "output" / "b.mp4").exists()

    def test_dry_run_does_not_delete_files(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings(), dry_run=True)
        _record_source(archive, {"id1", "id3"})
        archive.remove_entries_not_in_source()

        assert (tmp_path / "output" / "b.mp4").exists()

    def test_unenumerated_source_deletes_nothing(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings())
        archive.remove_entries_not_in_source()

        assert sorted(archive.mapping.entry_mappings.keys()) == ["id1", "id2", "id3"]
        assert (tmp_path / "output" / "b.mp4").exists()

    def test_truncated_source_deletes_nothing(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings())
        _record_source(archive, {"id1"})
        archive.mark_source_enumeration_truncated(reason="ExistingVideoReached")
        archive.remove_entries_not_in_source()

        assert sorted(archive.mapping.entry_mappings.keys()) == ["id1", "id2", "id3"]
        assert (tmp_path / "output" / "b.mp4").exists()


class TestSourceEntryIds:
    def test_defaults_to_none(self, tmp_path):
        assert _make_archive(tmp_path, {}).source_entry_ids is None

    def test_records_ids(self, tmp_path):
        archive = _make_archive(tmp_path, {})
        archive.record_source_entry_id(entry_id="id1")
        archive.record_source_entry_id(entry_id="id2")

        assert archive.source_entry_ids == {"id1", "id2"}

    def test_truncated_returns_none(self, tmp_path):
        archive = _make_archive(tmp_path, {})
        archive.record_source_entry_id(entry_id="id1")
        archive.mark_source_enumeration_truncated(reason="ExistingVideoReached")

        assert archive.source_entry_ids is None

    def test_truncation_is_not_undone_by_later_records(self, tmp_path):
        archive = _make_archive(tmp_path, {})
        archive.mark_source_enumeration_truncated(reason="ExistingVideoReached")
        archive.record_source_entry_id(entry_id="id1")

        assert archive.source_entry_ids is None


class TestSyncWithSourceOption:
    _base = {"output_directory": "/tmp/out", "file_name": "{title}.{ext}"}

    def test_defaults_to_disabled(self):
        assert OutputOptions("t", dict(self._base)).sync_with_source is None

    def test_enabled(self):
        options = OutputOptions(
            "t", self._base | {"maintain_download_archive": True, "sync_with_source": True}
        )
        assert options.sync_with_source.format_string == "True"

    def test_accepts_override(self):
        options = OutputOptions(
            "t", self._base | {"maintain_download_archive": True, "sync_with_source": "{my_flag}"}
        )
        assert options.sync_with_source.format_string == "{my_flag}"

    def test_requires_maintain_download_archive(self):
        with pytest.raises(ValidationException, match="maintain_download_archive"):
            OutputOptions("t", self._base | {"sync_with_source": True})

    @pytest.mark.parametrize(
        "keep_option, keep_value",
        [
            ("keep_files_before", "now"),
            ("keep_files_after", "19000101"),
            ("keep_max_files", 10),
        ],
    )
    def test_cannot_be_used_with_keep_options(self, keep_option, keep_value):
        with pytest.raises(ValidationException, match="cannot be used with"):
            OutputOptions(
                "t",
                self._base
                | {
                    "maintain_download_archive": True,
                    "sync_with_source": True,
                    keep_option: keep_value,
                },
            )


class TestExtractInfoViaInfoJsonEnumeration:
    @staticmethod
    def _base_ytdl_options() -> dict:
        return {
            "skip_download": True,
            "writethumbnail": False,
            "writeinfojson": True,
            "extract_flat": "discard",
            "ignoreerrors": True,
            "quiet": True,
        }

    def test_failed_playlist_entry_keeps_id_in_enumerated_ids(self, tmp_path):
        import json

        working_dir = tmp_path / "working"
        working_dir.mkdir()
        opts = self._base_ytdl_options() | {"outtmpl": str(working_dir / "%(id)S.%(ext)s")}

        def _fake_extract_info(ydl_self, **kwargs):
            _ = kwargs
            orig_process = ydl_self.process_ie_result

            def _fake_process(ie_result, download=True, extra_info=None):
                entry_id = ie_result.get("id")
                if entry_id == "v_fail":
                    raise DownloadError("formats have been skipped as they are missing a URL")
                if entry_id == "v_ok":
                    (working_dir / "v_ok.info.json").write_text(
                        json.dumps({"_type": "video", "id": "v_ok", "title": "OK", "ext": "mp4"}),
                        encoding="utf-8",
                    )
                    return {"_type": "video", "id": "v_ok", "title": "OK", "ext": "mp4"}
                return orig_process(ie_result, download=download, extra_info=extra_info)

            ydl_self.process_ie_result = _fake_process
            return ydl_self.process_ie_result(
                {
                    "_type": "playlist",
                    "id": "pl_1",
                    "title": "PL 1",
                    "extractor": "youtube:tab",
                    "extractor_key": "YoutubeTab",
                    "entries": [
                        {
                            "_type": "url",
                            "id": "v_ok",
                            "url": "https://www.youtube.com/watch?v=v_ok",
                            "ie_key": "Youtube",
                        },
                        {
                            "_type": "url",
                            "id": "v_fail",
                            "url": "https://www.youtube.com/watch?v=v_fail",
                            "ie_key": "Youtube",
                        },
                    ],
                },
                download=False,
            )

        truncation_reasons = []
        enumerated_ids = set()
        with patch.object(yt_dlp.YoutubeDL, "extract_info", new=_fake_extract_info):
            entry_dicts = YTDLP.extract_info_via_info_json(
                working_directory=str(working_dir),
                ytdl_options_overrides=opts,
                truncation_reasons=truncation_reasons,
                enumerated_entry_ids=enumerated_ids,
                url="https://www.youtube.com/playlist?list=pl_1",
            )

        assert sorted(d["id"] for d in entry_dicts) == ["pl_1", "v_ok"]
        assert enumerated_ids == {"v_ok", "v_fail"}
        assert truncation_reasons == []

    def test_nested_channel_tabs_record_leaf_ids_and_detect_failed_tab(self, tmp_path):
        working_dir = tmp_path / "working"
        working_dir.mkdir()
        opts = self._base_ytdl_options() | {"outtmpl": str(working_dir / "%(id)S.%(ext)s")}

        fail_shorts_tab = False

        def _fake_extract_info(ydl_self, **kwargs):
            _ = kwargs
            orig_process = ydl_self.process_ie_result

            def _fake_process(ie_result, download=True, extra_info=None):
                entry_id = ie_result.get("id")
                if entry_id == "tab_videos":
                    return orig_process(
                        {
                            "_type": "playlist",
                            "id": "tab_videos",
                            "extractor": "youtube:tab",
                            "extractor_key": "YoutubeTab",
                            "entries": [
                                {
                                    "_type": "url",
                                    "id": "v_ok",
                                    "url": "https://www.youtube.com/watch?v=v_ok",
                                    "ie_key": "Youtube",
                                },
                                {
                                    "_type": "url",
                                    "id": "v_fail",
                                    "url": "https://www.youtube.com/watch?v=v_fail",
                                    "ie_key": "Youtube",
                                },
                            ],
                        },
                        download=False,
                        extra_info=extra_info,
                    )
                if entry_id == "tab_shorts":
                    if fail_shorts_tab:
                        raise DownloadError("HTTP Error 429: Too Many Requests")
                    return orig_process(
                        {
                            "_type": "playlist",
                            "id": "tab_shorts",
                            "extractor": "youtube:tab",
                            "extractor_key": "YoutubeTab",
                            "entries": [
                                {
                                    "_type": "url",
                                    "id": "s_ok",
                                    "url": "https://www.youtube.com/watch?v=s_ok",
                                    "ie_key": "Youtube",
                                }
                            ],
                        },
                        download=False,
                        extra_info=extra_info,
                    )
                if entry_id == "v_fail":
                    raise DownloadError("Requested format is not available")
                if entry_id in ("v_ok", "s_ok"):
                    return {"_type": "video", "id": entry_id, "title": entry_id, "ext": "mp4"}
                return orig_process(ie_result, download=download, extra_info=extra_info)

            ydl_self.process_ie_result = _fake_process
            return ydl_self.process_ie_result(
                {
                    "_type": "playlist",
                    "id": "UC_chan",
                    "extractor": "youtube:tab",
                    "extractor_key": "YoutubeTab",
                    "entries": [
                        {
                            "_type": "url",
                            "id": "tab_videos",
                            "url": "https://www.youtube.com/@chan/videos",
                            "ie_key": "YoutubeTab",
                        },
                        {
                            "_type": "url",
                            "id": "tab_shorts",
                            "url": "https://www.youtube.com/@chan/shorts",
                            "ie_key": "YoutubeTab",
                        },
                    ],
                },
                download=False,
            )

        with patch.object(yt_dlp.YoutubeDL, "extract_info", new=_fake_extract_info):
            truncation_ok = []
            ids_ok = set()
            YTDLP.extract_info_via_info_json(
                working_directory=str(working_dir),
                ytdl_options_overrides=opts,
                truncation_reasons=truncation_ok,
                enumerated_entry_ids=ids_ok,
                url="https://www.youtube.com/@chan",
            )
            assert ids_ok == {"v_ok", "v_fail", "s_ok"}
            assert truncation_ok == []

            fail_shorts_tab = True
            truncation_err = []
            ids_err = set()
            YTDLP.extract_info_via_info_json(
                working_directory=str(working_dir),
                ytdl_options_overrides=opts,
                truncation_reasons=truncation_err,
                enumerated_entry_ids=ids_err,
                url="https://www.youtube.com/@chan",
            )
            assert ids_err == {"v_ok", "v_fail"}
            assert truncation_err == ["PlaylistExtractionFailed:tab_shorts"]

    def test_top_level_failure_returning_none_marks_truncation(self, tmp_path):
        working_dir = tmp_path / "working"
        working_dir.mkdir()
        opts = self._base_ytdl_options() | {"outtmpl": str(working_dir / "%(id)S.%(ext)s")}

        truncation_reasons = []
        enumerated_ids = set()
        with patch.object(yt_dlp.YoutubeDL, "extract_info", return_value=None):
            YTDLP.extract_info_via_info_json(
                working_directory=str(working_dir),
                ytdl_options_overrides=opts,
                truncation_reasons=truncation_reasons,
                enumerated_entry_ids=enumerated_ids,
                url="https://www.youtube.com/playlist?list=broken",
            )

        assert truncation_reasons == ["ExtractionFailed"]
        assert enumerated_ids == set()
