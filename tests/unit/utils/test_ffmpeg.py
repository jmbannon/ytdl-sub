import subprocess
from unittest.mock import patch

import pytest

from ytdl_sub.utils.exceptions import ValidationException
from ytdl_sub.utils.ffmpeg import (
    FFMPEG,
    _create_metadata_chapter_entry,
    _ffmpeg_metadata_escape,
)


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


class TestEnsureInstalled:
    def test_checks_installation_once(self, monkeypatch):
        monkeypatch.setattr(FFMPEG, "_FFMPEG_PATH", "ffmpeg")
        monkeypatch.setattr(FFMPEG, "_FFPROBE_PATH", "ffprobe")
        monkeypatch.setattr(FFMPEG, "_FFMPEG_INSTALLED", False)

        with patch("ytdl_sub.utils.ffmpeg.subprocess.check_output") as check_output:
            FFMPEG._ensure_installed()
            FFMPEG._ensure_installed()

        check_output.assert_called_once_with(["ffmpeg", "-version"])

    def test_set_paths_resets_the_cache(self, monkeypatch):
        monkeypatch.setattr(FFMPEG, "_FFMPEG_PATH", "ffmpeg")
        monkeypatch.setattr(FFMPEG, "_FFPROBE_PATH", "ffprobe")
        monkeypatch.setattr(FFMPEG, "_FFMPEG_INSTALLED", False)

        with patch("ytdl_sub.utils.ffmpeg.subprocess.check_output") as check_output:
            FFMPEG._ensure_installed()
            FFMPEG.set_paths(ffmpeg_path="ffmpeg-new", ffprobe_path="ffprobe-new")
            FFMPEG._ensure_installed()

        assert check_output.call_count == 2
        assert check_output.call_args_list[-1].args[0] == ["ffmpeg-new", "-version"]

    def test_failed_check_is_not_cached(self, monkeypatch):
        monkeypatch.setattr(FFMPEG, "_FFMPEG_PATH", "ffmpeg")
        monkeypatch.setattr(FFMPEG, "_FFMPEG_INSTALLED", False)

        with patch(
            "ytdl_sub.utils.ffmpeg.subprocess.check_output",
            side_effect=subprocess.CalledProcessError(returncode=1, cmd="ffmpeg"),
        ):
            with pytest.raises(ValidationException):
                FFMPEG._ensure_installed()

        assert FFMPEG._FFMPEG_INSTALLED is False
