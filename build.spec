# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/app.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'src.database',
        'src.version',
        'src.updater',
        'src.match_engine',
        'src.excel_importer',
        'src.exporter',
        'src.view_helpers',
        'src.dao',
        'src.dao.backend_dao',
        'src.dao.drama_dao',
        'src.dao.month_dao',
        'src.dao.imported_data_dao',
        'src.gui',
        'src.gui.main_window',
        'src.gui.backend_view',
        'src.gui.drama_library_dialog',
        'src.gui.month_view',
    ],
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
    name='DramaDataManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None,
)
