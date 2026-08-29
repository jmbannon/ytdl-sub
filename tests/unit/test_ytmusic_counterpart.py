import pytest

from ytdl_sub.downloaders.url.validators import UrlValidator
from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.ytdl_additions.enhanced_download_archive import (
    DownloadMapping,
    DownloadMappings,
    EnhancedDownloadArchive,
)


def _make_archive(tmp_path, mappings_dict):
    working = tmp_path / "working"
    output = tmp_path / "output"
    working.mkdir()
    output.mkdir()

    archive = EnhancedDownloadArchive(
        file_name="archive.json",
        working_directory=str(working),
        output_directory=str(output),
        dry_run=False,
    )
    archive._download_mapping = DownloadMappings()
    for uid, mapping in mappings_dict.items():
        archive._download_mapping._entry_mappings[uid] = mapping
        for file_name in mapping.file_names:
            (output / file_name).write_text("content")
    return archive


class TestDownloadMappingSourceUid:
    def test_source_uid_round_trips(self):
        mapping = DownloadMapping(
            upload_date="2024-01-01",
            extractor="youtube",
            file_names={"song.mp3"},
            source_uid="video_id",
        )
        assert mapping.dict["source_uid"] == "video_id"
        assert DownloadMapping.from_dict(mapping.dict).source_uid == "video_id"

    def test_source_uid_is_not_written_when_unset(self):
        """
        Archives without any swapped entries must serialize exactly as they did before,
        so upgrading does not rewrite every user's download archive.
        """
        mapping = DownloadMapping(
            upload_date="2024-01-01", extractor="youtube", file_names={"video.mp4"}
        )
        assert "source_uid" not in mapping.dict

    def test_archive_written_before_this_feature_still_loads(self):
        mapping = DownloadMapping.from_dict(
            {
                "upload_date": "2024-01-01",
                "extractor": "youtube",
                "file_names": ["video.mp4"],
                "playlist_index": 3,
            }
        )
        assert mapping.source_uid is None
        assert mapping.playlist_index == 3


class TestToDownloadArchive:
    def test_swapped_entry_records_both_ids(self, tmp_path):
        """
        The source enumerates the entry under its original id, so yt-dlp needs that one in
        the archive to skip it on the next run rather than re-resolving every entry.
        """
        archive = _make_archive(
            tmp_path,
            {
                "song_id": DownloadMapping(
                    "2024-01-01", "youtube", {"song.mp3"}, source_uid="video_id"
                )
            },
        )
        archive_file = tmp_path / "ytdl.archive"
        archive.mapping.to_download_archive().to_file(str(archive_file))

        lines = archive_file.read_text().splitlines()
        assert lines == ["youtube song_id", "youtube video_id"]

    def test_unswapped_entry_records_one_id(self, tmp_path):
        archive = _make_archive(
            tmp_path, {"video_id": DownloadMapping("2024-01-01", "youtube", {"video.mp4"})}
        )
        archive_file = tmp_path / "ytdl.archive"
        archive.mapping.to_download_archive().to_file(str(archive_file))

        assert archive_file.read_text().splitlines() == ["youtube video_id"]


class TestRemoveEntriesNotInSourceWithSwappedEntries:
    def test_entry_seen_under_its_source_uid_is_kept(self, tmp_path):
        """
        With sync_with_source, the archive is withheld from the metadata fetch, so the
        source enumerates the original video id while the archive is keyed by the song.
        """
        archive = _make_archive(
            tmp_path,
            {
                "song_id": DownloadMapping(
                    "2024-01-01", "youtube", {"song.mp3"}, source_uid="video_id"
                )
            },
        )
        archive.record_source_entry_id(entry_id="video_id")
        archive.remove_entries_not_in_source()

        assert list(archive.mapping.entry_mappings.keys()) == ["song_id"]
        assert (tmp_path / "output" / "song.mp3").exists()

    def test_entry_seen_under_its_own_uid_is_kept(self, tmp_path):
        archive = _make_archive(
            tmp_path,
            {
                "song_id": DownloadMapping(
                    "2024-01-01", "youtube", {"song.mp3"}, source_uid="video_id"
                )
            },
        )
        archive.record_source_entry_id(entry_id="song_id")
        archive.remove_entries_not_in_source()

        assert list(archive.mapping.entry_mappings.keys()) == ["song_id"]

    def test_entry_gone_from_source_under_either_id_is_pruned(self, tmp_path):
        archive = _make_archive(
            tmp_path,
            {
                "song_id": DownloadMapping(
                    "2024-01-01", "youtube", {"song.mp3"}, source_uid="video_id"
                )
            },
        )
        archive.record_source_entry_id(entry_id="some_other_id")
        archive.remove_entries_not_in_source()

        assert not archive.mapping.entry_mappings
        assert not (tmp_path / "output" / "song.mp3").exists()


class TestUrlValidatorOptions:
    def test_defaults_to_disabled(self):
        validator = UrlValidator("download", {"url": "https://music.youtube.com"})
        assert validator.ytmusic_counterpart.format_string == "disabled"
        assert validator.ytmusic_counterpart_when_missing.format_string == "original"

    @pytest.mark.parametrize("counterpart", ["song", "video", "disabled"])
    @pytest.mark.parametrize("when_missing", ["original", "skip"])
    def test_accepts_supported_values(self, counterpart: str, when_missing: str):
        validator = UrlValidator(
            "download",
            {
                "url": "https://music.youtube.com",
                "ytmusic_counterpart": counterpart,
                "ytmusic_counterpart_when_missing": when_missing,
            },
        )
        assert validator.ytmusic_counterpart.format_string == counterpart
        assert validator.ytmusic_counterpart_when_missing.format_string == when_missing

    @pytest.mark.parametrize(
        "key, value",
        [
            ("ytmusic_counterpart", "audio"),
            ("ytmusic_counterpart_when_missing", "download"),
        ],
        ids=["bad-counterpart", "bad-when-missing"],
    )
    def test_rejects_unsupported_values(self, key: str, value: str):
        """
        The values are override formatters, so they are only validated once resolved.
        """
        validator = UrlValidator("download", {"url": "https://music.youtube.com", key: value})

        with pytest.raises(ValidationException, match="Must be one of the following values"):
            getattr(validator, key).post_process(value)
