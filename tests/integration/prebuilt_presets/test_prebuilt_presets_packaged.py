class TestPrebuiltPresetsPackaged:
    def test_helpers_packaged(self) -> None:
        from ytdl_sub.prebuilt_presets.helpers import PREBUILT_PRESET_PACKAGE_NAME

        assert PREBUILT_PRESET_PACKAGE_NAME == "helpers"

    def test_internal_packaged(self) -> None:
        from ytdl_sub.prebuilt_presets.internal import PREBUILT_PRESET_PACKAGE_NAME

        assert PREBUILT_PRESET_PACKAGE_NAME == "internal"

    def test_music_packaged(self) -> None:
        from ytdl_sub.prebuilt_presets.music import PREBUILT_PRESET_PACKAGE_NAME

        assert PREBUILT_PRESET_PACKAGE_NAME == "music"

    def test_music_videos_packaged(self) -> None:
        from ytdl_sub.prebuilt_presets.music_videos import PREBUILT_PRESET_PACKAGE_NAME

        assert PREBUILT_PRESET_PACKAGE_NAME == "music_videos"

    def test_tv_show_packaged(self) -> None:
        from ytdl_sub.prebuilt_presets.tv_show import PREBUILT_PRESET_PACKAGE_NAME

        assert PREBUILT_PRESET_PACKAGE_NAME == "tv_show"
