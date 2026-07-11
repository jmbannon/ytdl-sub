import pytest

from ytdl_sub.validators.sort_by_validator import KeepMaxFilesSortByValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import (
    DownloadMapping,
    DownloadMappings,
    EnhancedDownloadArchive,
)


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

        remaining_ids = list(archive.mapping.entry_mappings.keys())
        assert sorted(remaining_ids) == ["id1", "id2", "id3"]

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

        remaining_ids = list(archive.mapping.entry_mappings.keys())
        assert sorted(remaining_ids) == ["id1", "id3", "id5"]

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

        remaining_ids = list(archive.mapping.entry_mappings.keys())
        assert sorted(remaining_ids) == ["id2", "id3", "id4"]

    def test_keep_max_zero_does_not_prune(self, tmp_path):
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}, playlist_index=1),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}, playlist_index=2),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}, playlist_index=3),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=0, sort_by="playlist_index_asc")

        remaining_ids = list(archive.mapping.entry_mappings.keys())
        assert sorted(remaining_ids) == ["id1", "id2", "id3"]


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

        remaining_ids = list(archive.mapping.entry_mappings.keys())
        assert sorted(remaining_ids) == ["id3", "id4", "id5"]

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

        remaining_ids = list(archive.mapping.entry_mappings.keys())
        assert sorted(remaining_ids) == ["id1", "id3", "id5"]

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

        remaining_ids = list(archive.mapping.entry_mappings.keys())
        assert sorted(remaining_ids) == ["id2", "id3", "id4"]

    def test_keep_max_zero_does_not_prune(self, tmp_path):
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}, playlist_index=1),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}, playlist_index=2),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}, playlist_index=3),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=0, sort_by="playlist_index_desc")

        remaining_ids = list(archive.mapping.entry_mappings.keys())
        assert sorted(remaining_ids) == ["id1", "id2", "id3"]


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

        remaining_ids = list(archive.mapping.entry_mappings.keys())
        assert sorted(remaining_ids) == ["id2", "id3", "id4"]

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

        remaining_ids = list(archive.mapping.entry_mappings.keys())
        assert sorted(remaining_ids) == ["id2", "id3", "id4"]
        for uid in remaining_ids:
            assert archive.mapping.entry_mappings[uid].playlist_index is None

    def test_keep_max_zero_does_not_prune(self, tmp_path):
        mappings = {
            "id1": DownloadMapping("2024-01-01", "yt", {"a.mp4"}),
            "id2": DownloadMapping("2024-01-02", "yt", {"b.mp4"}),
            "id3": DownloadMapping("2024-01-03", "yt", {"c.mp4"}),
        }
        archive = _make_archive(tmp_path, mappings)
        archive.remove_stale_files(date_range=None, keep_max_files=0, sort_by="upload_date")

        remaining_ids = list(archive.mapping.entry_mappings.keys())
        assert sorted(remaining_ids) == ["id1", "id2", "id3"]
