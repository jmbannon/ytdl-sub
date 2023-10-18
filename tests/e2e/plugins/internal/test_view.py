from typing import Optional

import pytest
from e2e.conftest import mock_run_from_cli

from ytdl_sub.utils.file_handler import FileMetadata


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
        subscription_transaction_log = mock_run_from_cli(args=args)

        assert len(subscription_transaction_log) == 1
        transaction_log = subscription_transaction_log[0][1]

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
