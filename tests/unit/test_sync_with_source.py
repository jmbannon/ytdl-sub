import pytest

from ytdl_sub.config.preset_options import OutputOptions
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
