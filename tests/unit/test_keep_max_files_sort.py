import pytest

from ytdl_sub.validators.sort_by_validator import KeepMaxFilesSortByValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import (
    DownloadMapping,
    DownloadMappings,
    EnhancedDownloadArchive,
)


def _active_ids(archive):
    return sorted(uid for uid, m in archive.mapping.entry_mappings.items() if not m.suppressed)


def _suppressed_ids(archive):
    return sorted(uid for uid, m in archive.mapping.entry_mappings.items() if m.suppressed)


class TestDownloadMappingPlaylistIndex:
    def test_from_dict_with_playlist_index(self):
        mapping = DownloadMapping.from_dict(
            {
                "upload_date": "2024-01-15",
                "extractor": "youtube",
                "file_names": ["video1.mp4"],
                "playlist_index": 5,
            }
        )
        assert mapping.playlist_index == 5
        assert isinstance(mapping.playlist_index, int)

    def test_from_dict_without_playlist_index_defaults_to_none(self):
        mapping = DownloadMapping.from_dict(
            {
                "upload_date": "2024-01-15",
                "extractor": "youtube",
                "file_names": ["video1.mp4"],
            }
        )
        assert mapping.playlist_index is None

    def test_dict_includes_playlist_index_when_present(self):
        mapping = DownloadMapping(
            upload_date="2024-01-15",
            extractor="youtube",
            file_names={"video1.mp4"},
            playlist_index=3,
        )
        result = mapping.dict
        assert result["playlist_index"] == 3

    def test_dict_includes_playlist_index_none_when_not_set(self):
        mapping = DownloadMapping(
            upload_date="2024-01-15",
            extractor="youtube",
            file_names={"video1.mp4"},
        )
        result = mapping.dict
        assert "playlist_index" in result
        assert result["playlist_index"] is None


class TestDownloadMappingSuppressed:
    def test_from_dict_without_suppressed_defaults_to_false(self):
        mapping = DownloadMapping.from_dict(
            {
                "upload_date": "2024-01-15",
                "extractor": "youtube",
                "file_names": ["video1.mp4"],
            }
        )
        assert mapping.suppressed is False

    def test_from_dict_with_suppressed(self):
        mapping = DownloadMapping.from_dict(
            {
                "upload_date": "2024-01-15",
                "extractor": "youtube",
                "file_names": [],
                "suppressed": True,
            }
        )
        assert mapping.suppressed is True

    def test_dict_omits_suppressed_when_false(self):
        mapping = DownloadMapping(
            upload_date="2024-01-15",
            extractor="youtube",
            file_names={"video1.mp4"},
        )
        assert "suppressed" not in mapping.dict

    def test_dict_includes_suppressed_when_true(self):
        mapping = DownloadMapping(
            upload_date="2024-01-15",
            extractor="youtube",
            file_names=set(),
            suppressed=True,
        )
        assert mapping.dict["suppressed"] is True


class TestKeepMaxFilesSortByValidator:
    def test_accepts_upload_date(self):
        validator = KeepMaxFilesSortByValidator(name="test", value="upload_date")
        assert validator.post_process("upload_date") == "upload_date"

    def test_accepts_playlist_index_asc(self):
        validator = KeepMaxFilesSortByValidator(name="test", value="playlist_index_asc")
        assert validator.post_process("playlist_index_asc") == "playlist_index_asc"

    def test_accepts_playlist_index_desc(self):
        validator = KeepMaxFilesSortByValidator(name="test", value="playlist_index_desc")
        assert validator.post_process("playlist_index_desc") == "playlist_index_desc"

    def test_rejects_invalid_value(self):
        from ytdl_sub.utils.exceptions import ValidationException

        validator = KeepMaxFilesSortByValidator(name="test", value="title")
        with pytest.raises(ValidationException, match="Must be one of the following values"):
            validator.post_process("title")

    def test_rejects_bare_playlist_index(self):
        from ytdl_sub.utils.exceptions import ValidationException

        validator = KeepMaxFilesSortByValidator(name="test", value="playlist_index")
        with pytest.raises(ValidationException, match="Must be one of the following values"):
            validator.post_process("playlist_index")


def _make_archive(tmp_path, mappings_dict):
    working = tmp_path / "working"
    output = tmp_path / "output"
    working.mkdir()
    output.mkdir()

    archive = EnhancedDownloadArchive(
        file_name="archive.json",
        working_directory=str(working),
        output_directory=str(output),
    )
    archive._download_mapping = DownloadMappings()
    for uid, mapping in mappings_dict.items():
        archive._download_mapping._entry_mappings[uid] = mapping
        for fname in mapping.file_names:
            (output / fname).write_text("content")
    return archive


class TestRemoveStaleFilesSortByPlaylistIndexAsc:
    def test_keeps_lowest_indices(self, tmp_path):
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}, playlist_index=1),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}, playlist_index=2),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}, playlist_index=3),
            "id4": DownloadMapping("2024-01-04", "yt", {"d.mp4"}, playlist_index=4),
            "id5": DownloadMapping("2024-01-05", "yt", {"e.mp4"}, playlist_index=5),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=3, sort_by="playlist_index_asc")

        assert _active_ids(archive) == ["id1", "id2", "id3"]
        assert _suppressed_ids(archive) == ["id4", "id5"]

    def test_prunes_none_first(self, tmp_path):
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}, playlist_index=1),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}, playlist_index=None),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}, playlist_index=3),
            "id4": DownloadMapping("2024-01-04", "yt", {"d.mp4"}, playlist_index=None),
            "id5": DownloadMapping("2024-01-05", "yt", {"e.mp4"}, playlist_index=5),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=3, sort_by="playlist_index_asc")

        assert _active_ids(archive) == ["id1", "id3", "id5"]
        assert _suppressed_ids(archive) == ["id2", "id4"]

    def test_all_none_falls_back_to_upload_date(self, tmp_path):
        from unittest.mock import patch

        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}, playlist_index=None),
            "id2": DownloadMapping("2024-01-05", "yt", {"b.mp4"}, playlist_index=None),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}, playlist_index=None),
            "id4": DownloadMapping("2024-01-04", "yt", {"d.mp4"}, playlist_index=None),
            "id5": DownloadMapping("2024-01-02", "yt", {"e.mp4"}, playlist_index=None),
        }
        archive = _make_archive(tmp_path, mappings)

        with patch("ytdl_sub.ytdl_additions.enhanced_download_archive.logger") as mock_logger:
            archive.remove_stale_files(
                date_range=None, keep_max_files=3, sort_by="playlist_index_asc"
            )
            mock_logger.warning.assert_called_once()
            assert "Falling back" in mock_logger.warning.call_args[0][0]

        assert _active_ids(archive) == ["id2", "id3", "id4"]
        assert _suppressed_ids(archive) == ["id1", "id5"]

    def test_keep_max_zero_does_not_prune(self, tmp_path):
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}, playlist_index=1),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}, playlist_index=2),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}, playlist_index=3),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=0, sort_by="playlist_index_asc")

        assert _active_ids(archive) == ["id1", "id2", "id3"]
        assert _suppressed_ids(archive) == []


class TestRemoveStaleFilesSortByPlaylistIndexDesc:
    def test_keeps_highest_indices(self, tmp_path):
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}, playlist_index=1),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}, playlist_index=2),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}, playlist_index=3),
            "id4": DownloadMapping("2024-01-04", "yt", {"d.mp4"}, playlist_index=4),
            "id5": DownloadMapping("2024-01-05", "yt", {"e.mp4"}, playlist_index=5),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=3, sort_by="playlist_index_desc")

        assert _active_ids(archive) == ["id3", "id4", "id5"]
        assert _suppressed_ids(archive) == ["id1", "id2"]

    def test_prunes_none_first(self, tmp_path):
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}, playlist_index=1),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}, playlist_index=None),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}, playlist_index=3),
            "id4": DownloadMapping("2024-01-04", "yt", {"d.mp4"}, playlist_index=None),
            "id5": DownloadMapping("2024-01-05", "yt", {"e.mp4"}, playlist_index=5),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=3, sort_by="playlist_index_desc")

        assert _active_ids(archive) == ["id1", "id3", "id5"]
        assert _suppressed_ids(archive) == ["id2", "id4"]

    def test_all_none_falls_back_to_upload_date(self, tmp_path):
        from unittest.mock import patch

        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}, playlist_index=None),
            "id2": DownloadMapping("2024-01-05", "yt", {"b.mp4"}, playlist_index=None),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}, playlist_index=None),
            "id4": DownloadMapping("2024-01-04", "yt", {"d.mp4"}, playlist_index=None),
            "id5": DownloadMapping("2024-01-02", "yt", {"e.mp4"}, playlist_index=None),
        }
        archive = _make_archive(tmp_path, mappings)

        with patch("ytdl_sub.ytdl_additions.enhanced_download_archive.logger") as mock_logger:
            archive.remove_stale_files(
                date_range=None, keep_max_files=3, sort_by="playlist_index_desc"
            )
            mock_logger.warning.assert_called_once()
            assert "Falling back" in mock_logger.warning.call_args[0][0]

        assert _active_ids(archive) == ["id2", "id3", "id4"]
        assert _suppressed_ids(archive) == ["id1", "id5"]

    def test_keep_max_zero_does_not_prune(self, tmp_path):
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}, playlist_index=1),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}, playlist_index=2),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}, playlist_index=3),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=0, sort_by="playlist_index_desc")

        assert _active_ids(archive) == ["id1", "id2", "id3"]
        assert _suppressed_ids(archive) == []


class TestRemoveStaleFilesUploadDate:
    def test_keeps_most_recent(self, tmp_path):
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}, playlist_index=1),
            "id2": DownloadMapping("2024-01-05", "yt", {"b.mp4"}, playlist_index=2),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}, playlist_index=3),
            "id4": DownloadMapping("2024-01-04", "yt", {"d.mp4"}, playlist_index=4),
            "id5": DownloadMapping("2024-01-02", "yt", {"e.mp4"}, playlist_index=5),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=3, sort_by="upload_date")

        assert _active_ids(archive) == ["id2", "id3", "id4"]
        assert _suppressed_ids(archive) == ["id1", "id5"]

    def test_old_archive_without_playlist_index_sorts_by_upload_date(self, tmp_path):
        mappings = {
            "id1": DownloadMapping.from_dict(
                {"upload_date": "2024-01-01", "extractor": "yt", "file_names": ["a.mp4"]}
            ),
            "id2": DownloadMapping.from_dict(
                {"upload_date": "2024-01-05", "extractor": "yt", "file_names": ["b.mp4"]}
            ),
            "id3": DownloadMapping.from_dict(
                {"upload_date": "2024-01-03", "extractor": "yt", "file_names": ["c.mp4"]}
            ),
            "id4": DownloadMapping.from_dict(
                {"upload_date": "2024-01-04", "extractor": "yt", "file_names": ["d.mp4"]}
            ),
            "id5": DownloadMapping.from_dict(
                {"upload_date": "2024-01-02", "extractor": "yt", "file_names": ["e.mp4"]}
            ),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=3)

        assert _active_ids(archive) == ["id2", "id3", "id4"]
        for uid in ["id2", "id3", "id4"]:
            assert archive.mapping.entry_mappings[uid].playlist_index is None

    def test_keep_max_zero_does_not_prune(self, tmp_path):
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=0, sort_by="upload_date")

        assert _active_ids(archive) == ["id1", "id2", "id3"]
        assert _suppressed_ids(archive) == []


class TestSuppressedEntriesPreventRedownload:
    def test_suppressed_entries_in_download_archive(self, tmp_path):
        """Suppressed entries should appear in the yt-dlp download archive."""
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}),
            "id2": DownloadMapping("2024-01-05", "yt", {"b.mp4"}),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=2, sort_by="upload_date")

        assert _active_ids(archive) == ["id2", "id3"]
        assert _suppressed_ids(archive) == ["id1"]

        dl_archive = archive.mapping.to_download_archive()
        archive_lines = dl_archive._download_archive_lines
        archive_text = " ".join(archive_lines)
        assert "id1" in archive_text
        assert "id2" in archive_text
        assert "id3" in archive_text

    def test_suppressed_entries_not_recounted_on_subsequent_prune(self, tmp_path):
        """Already-suppressed entries should not count toward keep_max_files."""
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", set(), suppressed=True),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}),
            "id4": DownloadMapping("2024-01-04", "yt", {"d.mp4"}),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=2, sort_by="upload_date")

        assert _active_ids(archive) == ["id3", "id4"]
        assert _suppressed_ids(archive) == ["id1", "id2"]

    def test_suppressed_entry_files_deleted(self, tmp_path):
        """Files for suppressed entries should be deleted from disk."""
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}),
            "id2": DownloadMapping("2024-01-05", "yt", {"b.mp4"}),
        }
        archive = _make_archive(tmp_path, mappings)
        output = tmp_path / "output"
        assert (output / "a.mp4").exists()

        archive.remove_stale_files(date_range=None, keep_max_files=1, sort_by="upload_date")

        assert not (output / "a.mp4").exists()
        assert (output / "b.mp4").exists()

    def test_suppress_then_serialize_roundtrip(self, tmp_path):
        """Suppressed flag should survive JSON serialization roundtrip."""
        mappings = DownloadMappings()
        mappings._entry_mappings["id1"] = DownloadMapping(
            "2024-01-01", "yt", set(), suppressed=True
        )
        mappings._entry_mappings["id2"] = DownloadMapping(
            "2024-01-05", "yt", {"b.mp4"}, suppressed=False
        )

        json_path = str(tmp_path / "mappings.json")
        mappings.to_file(json_path)
        loaded = DownloadMappings.from_file(json_path)

        assert loaded._entry_mappings["id1"].suppressed is True
        assert loaded._entry_mappings["id1"].file_names == set()
        assert loaded._entry_mappings["id2"].suppressed is False
        assert loaded._entry_mappings["id2"].file_names == {"b.mp4"}
