from typing import Optional

import pytest
from conftest import mock_run_from_cli
from resources import DISABLE_YOUTUBE_TESTS

from ytdl_sub.utils.file_handler import FileMetadata


@pytest.mark.skipif(DISABLE_YOUTUBE_TESTS, reason="YouTube tests cannot run in GH")
class TestView:
    @pytest.mark.parametrize("split_chapters", [True, False])
    def test_view_from_cli(
        self,
        output_directory,
        split_chapters,
    ):

        args = f"view "
        args += "--split-chapters " if split_chapters else ""
        args += f"https://www.youtube.com/playlist?list=PLBsm_SagFMmdWnCnrNtLjA9kzfrRkto4i"
        subscriptions = mock_run_from_cli(args=args)

        assert len(subscriptions) == 1
        transaction_log = subscriptions[0].transaction_log

        # Ensure the video and thumbnail are recognized
        assert len(transaction_log.files_created) == 2

        video_metadata: Optional[FileMetadata] = None
        for file_name, metadata in transaction_log.files_created.items():
            if file_name.endswith("webm"):
                video_metadata = metadata
                break

        assert video_metadata is not None
        assert "Source Variables:" in video_metadata.metadata
        if split_chapters:
            assert "  chapter_index: 1" in video_metadata.metadata
        else:
            assert "  chapter_index: 1" not in video_metadata.metadata
