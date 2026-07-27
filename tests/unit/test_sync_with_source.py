from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from ytdl_sub.config.preset_options import OutputOptions
from ytdl_sub.subscriptions.subscription_download import SubscriptionDownload
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


def _mappings():
    return {
        "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}),
        "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}),
        "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}),
    }


class TestRemoveEntriesNotInSource:
    def test_entry_removed_from_source_is_pruned(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings())
        archive.remove_entries_not_in_source(source_entry_ids={"id1", "id3"})

        assert sorted(archive.mapping.entry_mappings.keys()) == ["id1", "id3"]
        assert not (tmp_path / "output" / "b.mp4").exists()

    def test_entry_still_in_source_is_untouched(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings())
        archive.remove_entries_not_in_source(source_entry_ids={"id1", "id3"})

        assert (tmp_path / "output" / "a.mp4").exists()
        assert (tmp_path / "output" / "c.mp4").exists()
        assert archive.num_entries_removed == 1

    def test_all_entries_in_source_removes_nothing(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings())
        archive.remove_entries_not_in_source(source_entry_ids={"id1", "id2", "id3"})

        assert sorted(archive.mapping.entry_mappings.keys()) == ["id1", "id2", "id3"]
        assert archive.num_entries_removed == 0

    def test_source_with_new_entries_removes_nothing(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings())
        archive.remove_entries_not_in_source(source_entry_ids={"id1", "id2", "id3", "id4"})

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
        archive.remove_entries_not_in_source(source_entry_ids={"id2"})

        for file_name in ("a.mp4", "a.nfo", "a-thumb.jpg", "a.info.json"):
            assert not (tmp_path / "output" / file_name).exists()
        assert (tmp_path / "output" / "b.mp4").exists()

    def test_dry_run_does_not_delete_files(self, tmp_path):
        archive = _make_archive(tmp_path, _mappings(), dry_run=True)
        archive.remove_entries_not_in_source(source_entry_ids={"id1", "id3"})

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


class _FakeOverrides:
    def apply_formatter(self, formatter, expected_type=None, entry=None):
        _ = formatter, expected_type, entry
        return True


def _subscription_stub(tmp_path, source_entry_ids, sync_enabled: bool = True):
    download_archive = MagicMock()
    download_archive.source_entry_ids = source_entry_ids
    download_archive.working_ytdl_file_path = str(tmp_path / "working.ytdl")

    return SimpleNamespace(
        maintain_download_archive=True,
        download_archive=download_archive,
        overrides=_FakeOverrides(),
        output_options=SimpleNamespace(
            sync_with_source=object() if sync_enabled else None,
            keep_files_before=None,
            keep_files_after=None,
            keep_max_files=None,
            keep_max_files_sort_by=None,
        ),
    )


class TestMaintainArchiveFileSyncGuard:
    @classmethod
    def _run(cls, stub):
        with SubscriptionDownload._maintain_archive_file(stub):
            pass

    def test_prunes_when_source_enumerated(self, tmp_path):
        stub = _subscription_stub(tmp_path, source_entry_ids={"id1"})
        self._run(stub)

        stub.download_archive.remove_entries_not_in_source.assert_called_once_with(
            source_entry_ids={"id1"}
        )

    def test_does_not_prune_when_enumeration_failed(self, tmp_path):
        stub = _subscription_stub(tmp_path, source_entry_ids=None)

        with patch("ytdl_sub.subscriptions.subscription_download.logger") as mock_logger:
            self._run(stub)
            assert "not fully enumerated" in mock_logger.warning.call_args[0][0]

        stub.download_archive.remove_entries_not_in_source.assert_not_called()

    def test_does_not_prune_when_source_is_empty(self, tmp_path):
        stub = _subscription_stub(tmp_path, source_entry_ids=set())

        with patch("ytdl_sub.subscriptions.subscription_download.logger") as mock_logger:
            self._run(stub)
            assert "zero entries" in mock_logger.warning.call_args[0][0]

        stub.download_archive.remove_entries_not_in_source.assert_not_called()

    def test_disabled_by_default(self, tmp_path):
        stub = _subscription_stub(tmp_path, source_entry_ids={"id1"}, sync_enabled=False)
        self._run(stub)

        stub.download_archive.remove_entries_not_in_source.assert_not_called()
