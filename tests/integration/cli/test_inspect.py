from pathlib import Path

import pytest
import yaml
from conftest import mock_run_from_cli


class TestInspect:
    @pytest.mark.parametrize("config_provided", [True, False])
    def test_inspect_command(
        self,
        capsys,
        default_config_path: str,
        tv_show_subscriptions_path: Path,
        output_directory: str,
        config_provided: bool,
    ):
        args = f"--config {default_config_path} " if config_provided else ""
        args += f"inspect {tv_show_subscriptions_path} --match 'Jake Trains'"

        subscriptions = mock_run_from_cli(args=args)
        assert len(subscriptions) == 0

        captured_as_dict = yaml.safe_load(capsys.readouterr().out)
        assert captured_as_dict == {
            "chapters": {
                "allow_chapters_from_comments": False,
                "embed_chapters": True,
                "enable": "True",
                "force_key_frames": False,
            },
            "date_range": {"breaks": "True", "enable": "True", "type": "upload_date"},
            "download": [
                {
                    "download_reverse": "True",
                    "include_sibling_metadata": False,
                    "playlist_thumbnails": [
                        {
                            "name": "{avatar_uncropped_thumbnail_file_name}",
                            "uid": "avatar_uncropped",
                        },
                        {
                            "name": "{banner_uncropped_thumbnail_file_name}",
                            "uid": "banner_uncropped",
                        },
                    ],
                    "source_thumbnails": [
                        {
                            "name": "{avatar_uncropped_thumbnail_file_name}",
                            "uid": "avatar_uncropped",
                        },
                        {
                            "name": "{banner_uncropped_thumbnail_file_name}",
                            "uid": "banner_uncropped",
                        },
                    ],
                    "url": "https://www.youtube.com/@JakeTrains",
                    "variables": {},
                    "webpage_url": "{modified_webpage_url}",
                    "ytdl_options": {},
                }
            ],
            "file_convert": {"convert_to": "mp4", "convert_with": "yt-dlp", "enable": "True"},
            "format": "(bv*[ext=mp4][vcodec~='^((he|a)vc|h26[45])']+ba[ext=m4a]) / (bv[ext=mp4]*+ba[ext=m4a]/b)",
            "output_options": {
                "download_archive_name": ".ytdl-sub-Jake Trains-download-archive.json",
                "file_name": "{episode_file_path}.{ext}",
                "info_json_name": "{episode_file_path}.{info_json_ext}",
                "keep_files_date_eval": "{episode_date_standardized}",
                "maintain_download_archive": True,
                "output_directory": f"{output_directory}/Jake Trains",
                "preserve_mtime": False,
                "thumbnail_name": "{thumbnail_file_name}",
            },
            "throttle_protection": {
                "enable": True,
                "sleep_per_download_s": {"max": "28.4", "min": "13.8"},
                "sleep_per_request_s": {"max": "0.75", "min": "0.0"},
                "sleep_per_subscription_s": {"max": "26.1", "min": "16.3"},
            },
            "video_tags": {
                "contentRating": "{episode_content_rating}",
                "date": "{episode_date_standardized}",
                "episode_id": "{episode_number}",
                "genre": "{tv_show_genre}",
                "show": "{tv_show_name}",
                "synopsis": "{episode_plot}",
                "title": "{episode_title}",
                "year": "{episode_year}",
            },
        }
