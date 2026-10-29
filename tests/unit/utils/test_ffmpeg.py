import pytest

from ytdl_sub.utils.ffmpeg import _create_metadata_chapter_entry, _ffmpeg_metadata_escape


class TestFFMPEGMetadataEscape:
    @pytest.mark.parametrize(
        "metadata, expected",
        [
            ("Intro", "Intro"),
            # every character ffmpeg treats specially in ffmetadata values
            ("A = B", r"A \= B"),
            ("A ; B", r"A \; B"),
            ("A # B", r"A \# B"),
            (r"A \ B", r"A \\ B"),
            ("A\nB", "A\\\nB"),
            # adjacent special characters must each be escaped exactly once
            ("=;#", r"\=\;\#"),
            # a backslash directly before a special character must not eat it
            (r"a\=b", r"a\\\=b"),
            # real-world title with several different special characters
            (r"C:\path=a;b#c", r"C:\\path\=a\;b\#c"),
            ("", ""),
        ],
    )
    def test_escape_metadata(self, metadata: str, expected: str):
        assert _ffmpeg_metadata_escape(metadata) == expected


class TestCreateMetadataChapterEntry:
    def test_escaped_title_in_chapter_entry(self):
        assert _create_metadata_chapter_entry(start_sec=0, end_sec=10, title="A = B") == [
            "",
            "[CHAPTER]",
            "TIMEBASE=1/1000",
            "START=0",
            "END=10000",
            r"title=A \= B",
        ]
