from yt_dlp import DateRange

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
    )
    archive._download_mapping = DownloadMappings()
    for uid, mapping in mappings_dict.items():
        archive._download_mapping._entry_mappings[uid] = mapping
        for file_name in mapping.file_names:
            (output / file_name).write_text("content")
    return archive


class TestSaveDownloadMappings:
    def test_mapping_changes_are_saved_without_file_transactions(self, tmp_path):
        archive = _make_archive(
            tmp_path,
            {
                "old": DownloadMapping("2024-01-01", "youtube", {"old.mp4"}),
                "new": DownloadMapping("2024-06-01", "youtube", {"new.mp4"}),
            },
        )

        # Simulate the old file being removed externally before its archive entry goes stale
        (tmp_path / "output" / "old.mp4").unlink()

        archive.remove_stale_files(
            date_range=DateRange(start="20240201"),
            keep_max_files=None,
        )
        assert archive.num_entries_removed == 1

        archive.save_download_mappings()

        saved_mapping = DownloadMappings.from_file(str(tmp_path / "output" / "archive.json"))
        assert saved_mapping.entry_ids == ["new"]

    def test_unchanged_mapping_and_files_are_not_saved(self, tmp_path):
        archive = _make_archive(
            tmp_path,
            {"id1": DownloadMapping("2024-01-01", "youtube", {"video.mp4"})},
        )

        archive.save_download_mappings()

        assert not (tmp_path / "output" / "archive.json").exists()
