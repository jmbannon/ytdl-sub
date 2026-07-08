import pytest

from ytdl_sub.validators.sort_by_validator import KeepMaxFilesSortByValidator
from ytdl_sub.ytdl_additions.enhanced_download_archive import DownloadMapping


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

    def test_accepts_playlist_index(self):
        validator = KeepMaxFilesSortByValidator(name="test", value="playlist_index")
        assert validator.post_process("playlist_index") == "playlist_index"

    def test_rejects_invalid_value(self):
        from ytdl_sub.utils.exceptions import ValidationException

        validator = KeepMaxFilesSortByValidator(name="test", value="title")
        with pytest.raises(ValidationException, match="Must be one of the following values"):
            validator.post_process("title")
