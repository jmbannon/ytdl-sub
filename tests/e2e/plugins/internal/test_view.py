import pytest
from e2e.conftest import mock_run_from_cli


class TestView:
    @pytest.mark.parametrize("split_chapters", [True, False])
    def test_view_from_cli(
        self,
        music_video_config_path,
        output_directory,
        split_chapters,
    ):

        args = f"--config {music_video_config_path} view "
        args += "--split-chapters " if split_chapters else ""
        args += f"https://www.youtube.com/playlist?list=PLBsm_SagFMmdWnCnrNtLjA9kzfrRkto4i"
        subscription_transaction_log = mock_run_from_cli(args=args)

        assert len(subscription_transaction_log) == 1
        transaction_log = subscription_transaction_log[0][1]

        # Ensure the video and thumbnail are recognized
        assert len(transaction_log.files_created) == 2

        file_name = f"avUT-zd9v68{'___0' if split_chapters else ''}.webm"
        video_file = transaction_log.files_created.get(file_name)
        assert video_file is not None

        assert "Source Variables:" in video_file.metadata
        if split_chapters:
            assert "  chapter_index: 1" in video_file.metadata
        else:
            assert "  chapter_index: 1" not in video_file.metadata
