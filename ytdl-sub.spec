# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['src/ytdl_sub/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ytdl_sub/prebuilt_presets/helpers/*.yaml', 'ytdl_sub/prebuilt_presets/helpers'),
        ('src/ytdl_sub/prebuilt_presets/internal/*.yaml', 'ytdl_sub/prebuilt_presets/internal'),
        ('src/ytdl_sub/prebuilt_presets/music_videos/*.yaml', 'ytdl_sub/prebuilt_presets/music_videos'),
        ('src/ytdl_sub/prebuilt_presets/tv_show/*.yaml', 'ytdl_sub/prebuilt_presets/tv_show'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ytdl-sub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
