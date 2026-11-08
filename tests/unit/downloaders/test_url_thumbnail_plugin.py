from pathlib import Path
from typing import Optional

from ytdl_sub.config.overrides import Overrides
from ytdl_sub.downloaders.url.downloader import MultiUrlDownloader
from ytdl_sub.downloaders.url.validators import (
    MultiUrlValidator,
    UrlValidator,
)
from ytdl_sub.downloaders.ytdl_options_builder import YTDLOptionsBuilder
from ytdl_sub.entries.entry_parent import EntryParent
from ytdl_sub.ytdl_additions.enhanced_download_archive import EnhancedDownloadArchive


class TestUrlDownloaderThumbnailMetadata:
    """Tests for downloading channel thumbnails during metadata collection phase."""

    def _make_downloader(self, tmp_path, dry_run: bool = False):
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

        overrides = Overrides(name="overrides", value={})

        options = MultiUrlValidator(
            name="download",
            value={
                "urls": [{"url": "https://example.com/test"}],
            },
        )

        downloader = MultiUrlDownloader(
            options=options,
            enhanced_download_archive=archive,
            download_ytdl_options=YTDLOptionsBuilder(),
            metadata_ytdl_options=YTDLOptionsBuilder(),
            overrides=overrides,
        )
        return downloader, working, output

    def _make_parent(
        self,
        uid: str,
        thumbnails: list,
    ) -> EntryParent:
        entry_dict = {
            "id": uid,
            "uid": uid,
            "title": f"Parent {uid}",
            "webpage_url": f"https://example.com/{uid}",
            "thumbnails": thumbnails,
            "_type": "playlist",
        }
        return EntryParent(entry_dict=entry_dict, working_directory=".")

    def _make_url_validator(
        self,
        source_thumbnails: Optional[list] = None,
        playlist_thumbnails: Optional[list] = None,
    ) -> UrlValidator:
        value: dict = {"url": "https://example.com/test"}
        if source_thumbnails is not None:
            value["source_thumbnails"] = source_thumbnails
        if playlist_thumbnails is not None:
            value["playlist_thumbnails"] = playlist_thumbnails
        return UrlValidator(name="url", value=value)

    def test_downloads_parent_thumbnails_during_metadata_phase(self, tmp_path, monkeypatch):
        downloader, working, output = self._make_downloader(tmp_path)

        parent = self._make_parent(
            "channel_uid",
            [
                {"id": "avatar_uncropped", "url": "https://example.com/avatar.jpg"},
                {"id": "banner_uncropped", "url": "https://example.com/banner.jpg"},
            ],
        )

        validator = self._make_url_validator(
            source_thumbnails=[
                {"name": "poster.jpg", "uid": "avatar_uncropped"},
                {"name": "fanart.jpg", "uid": "banner_uncropped"},
            ],
        )

        converted = {}

        def fake_download(thumbnail_url, output_thumbnail_path, user_agent=None):
            converted[thumbnail_url] = output_thumbnail_path
            Path(output_thumbnail_path).write_bytes(b"fake-image")
            return True

        monkeypatch.setattr(
            "ytdl_sub.downloaders.url.downloader.download_and_convert_url_thumbnail",
            fake_download,
        )
        monkeypatch.setattr(downloader, "save_file", lambda *a, **k: None)

        downloader._download_parent_thumbnails_metadata(
            parents=[parent],
            collection_url=validator,
        )

        assert "https://example.com/avatar.jpg" in converted
        assert "https://example.com/banner.jpg" in converted
        assert (working / "poster.jpg").exists()
        assert (working / "fanart.jpg").exists()

    def test_skips_existing_files(self, tmp_path, monkeypatch):
        downloader, working, output = self._make_downloader(tmp_path)

        # Pre-create the output file
        (output / "poster.jpg").write_bytes(b"existing")

        parent = self._make_parent(
            "channel_uid",
            [{"id": "avatar_uncropped", "url": "https://example.com/avatar.jpg"}],
        )

        validator = self._make_url_validator(
            source_thumbnails=[{"name": "poster.jpg", "uid": "avatar_uncropped"}],
        )

        download_called = False

        def fake_download(thumbnail_url, output_thumbnail_path, user_agent=None):
            nonlocal download_called
            download_called = True
            return True

        monkeypatch.setattr(
            "ytdl_sub.downloaders.url.downloader.download_and_convert_url_thumbnail",
            fake_download,
        )
        monkeypatch.setattr(downloader, "save_file", lambda *a, **k: None)

        downloader._download_parent_thumbnails_metadata(
            parents=[parent],
            collection_url=validator,
        )

        assert not download_called

    def test_skips_when_thumbnail_id_not_found(self, tmp_path, monkeypatch):
        downloader, working, output = self._make_downloader(tmp_path)

        parent = self._make_parent(
            "channel_uid",
            [{"id": "other_id", "url": "https://example.com/other.jpg"}],
        )

        validator = self._make_url_validator(
            source_thumbnails=[{"name": "poster.jpg", "uid": "avatar_uncropped"}],
        )

        download_called = False

        def fake_download(thumbnail_url, output_thumbnail_path, user_agent=None):
            nonlocal download_called
            download_called = True
            return True

        monkeypatch.setattr(
            "ytdl_sub.downloaders.url.downloader.download_and_convert_url_thumbnail",
            fake_download,
        )
        monkeypatch.setattr(downloader, "save_file", lambda *a, **k: None)

        downloader._download_parent_thumbnails_metadata(
            parents=[parent],
            collection_url=validator,
        )

        assert not download_called

    def test_empty_parents_does_nothing(self, tmp_path, monkeypatch):
        downloader, working, output = self._make_downloader(tmp_path)

        validator = self._make_url_validator(
            source_thumbnails=[{"name": "poster.jpg", "uid": "avatar_uncropped"}],
        )

        download_called = False

        def fake_download(thumbnail_url, output_thumbnail_path, user_agent=None):
            nonlocal download_called
            download_called = True
            return True

        monkeypatch.setattr(
            "ytdl_sub.downloaders.url.downloader.download_and_convert_url_thumbnail",
            fake_download,
        )

        downloader._download_parent_thumbnails_metadata(
            parents=[],
            collection_url=validator,
        )

        assert not download_called

    def test_skips_empty_thumbnail_name(self, tmp_path, monkeypatch):
        downloader, working, output = self._make_downloader(tmp_path)

        parent = self._make_parent(
            "channel_uid",
            [{"id": "avatar_uncropped", "url": "https://example.com/avatar.jpg"}],
        )

        validator = self._make_url_validator(
            source_thumbnails=[{"name": "", "uid": "avatar_uncropped"}],
        )

        download_called = False

        def fake_download(thumbnail_url, output_thumbnail_path, user_agent=None):
            nonlocal download_called
            download_called = True
            return True

        monkeypatch.setattr(
            "ytdl_sub.downloaders.url.downloader.download_and_convert_url_thumbnail",
            fake_download,
        )
        monkeypatch.setattr(downloader, "save_file", lambda *a, **k: None)

        downloader._download_parent_thumbnails_metadata(
            parents=[parent],
            collection_url=validator,
        )

        assert not download_called

    def test_skips_latest_entry_in_metadata_phase(self, tmp_path, monkeypatch):
        downloader, working, output = self._make_downloader(tmp_path)

        parent = self._make_parent(
            "channel_uid",
            [{"id": "avatar_uncropped", "url": "https://example.com/avatar.jpg"}],
        )

        validator = self._make_url_validator(
            source_thumbnails=[
                {"name": "latest.jpg", "uid": "latest_entry"},
                {"name": "poster.jpg", "uid": "avatar_uncropped"},
            ],
        )

        download_called = False

        def fake_download(thumbnail_url, output_thumbnail_path, user_agent=None):
            nonlocal download_called
            download_called = True
            return True

        monkeypatch.setattr(
            "ytdl_sub.downloaders.url.downloader.download_and_convert_url_thumbnail",
            fake_download,
        )
        monkeypatch.setattr(downloader, "save_file", lambda *a, **k: None)

        downloader._download_parent_thumbnails_metadata(
            parents=[parent],
            collection_url=validator,
        )

        # Should skip latest_entry and download poster.jpg
        assert download_called

    def test_thumbnails_downloaded_before_entries_are_iterated(self, tmp_path, monkeypatch):
        downloader, working, output = self._make_downloader(tmp_path)

        parent = self._make_parent(
            "channel_uid",
            [{"id": "avatar_uncropped", "url": "https://example.com/avatar.jpg"}],
        )
        validator = self._make_url_validator(
            source_thumbnails=[{"name": "poster.jpg", "uid": "avatar_uncropped"}],
        )
        calls = []

        monkeypatch.setattr(
            downloader,
            "_download_url_metadata",
            lambda **kwargs: ([parent], []),
        )
        monkeypatch.setattr(
            downloader,
            "_download_parent_thumbnails_metadata",
            lambda **kwargs: calls.append("thumbnails"),
        )

        def fake_iterate_entries(**kwargs):
            calls.append("entries")
            return iter(())

        monkeypatch.setattr(downloader, "_iterate_entries", fake_iterate_entries)

        list(downloader._download_metadata(url="https://example.com/test", validator=validator))

        # Thumbnails must be downloaded even when no entries survive filtering.
        assert calls == ["thumbnails", "entries"]

    def test_dry_run_does_not_write_output(self, tmp_path, monkeypatch):
        downloader, working, output = self._make_downloader(tmp_path, dry_run=True)

        parent = self._make_parent(
            "channel_uid",
            [{"id": "avatar_uncropped", "url": "https://example.com/avatar.jpg"}],
        )
        validator = self._make_url_validator(
            source_thumbnails=[{"name": "poster.jpg", "uid": "avatar_uncropped"}],
        )

        def fake_download(thumbnail_url, output_thumbnail_path, user_agent=None):
            Path(output_thumbnail_path).write_bytes(b"fake-image")
            return True

        monkeypatch.setattr(
            "ytdl_sub.downloaders.url.downloader.download_and_convert_url_thumbnail",
            fake_download,
        )

        downloader._download_parent_thumbnails_metadata(
            parents=[parent],
            collection_url=validator,
        )

        assert not (output / "poster.jpg").exists()
