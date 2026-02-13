# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/app.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=['src.dao', 'src.gui'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='剧名数据管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)
